#!/usr/bin/env python3
"""
Core interpreter class with modular execution handlers.
"""

from AST.ASTNodes import *
from AST.semantic_analyzer import SemanticAnalyzer
from AST.ASTsymbol_table import SymbolKind
from errors.runtime_errors import SaltinoRuntimeError
from execution_frames import ExecutionFrame, FrameType
from execution_environment import Environment
from saltino_operators import SaltinoOperators
from typing import Any, List, Optional
import execution_handlers as handlers
from io_handler import get_main_arguments
from saltino_parser import parse_saltino


class IterativeSaltinoInterpreter:
    """
    Interprete Iterativo per il linguaggio Saltino con supporto per analisi semantica.

    Utilizza uno stack di frame di esecuzione per eliminare la ricorsione
    e gestire l'esecuzione in modo iterativo. Integra il SemanticAnalyzer
    per utilizzare nomi univoci e informazioni di scope.
    """

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.global_env = Environment(scope_name="global")
        self.execution_stack: List[ExecutionFrame] = []
        self.result_stack: List[Any] = []
        # Analizzatore semantico
        self.semantic_analyzer: Optional[SemanticAnalyzer] = None

        # Monitoraggio dello stack per l'analisi TCO
        self.max_stack_depth = 0
        self.function_call_count = 0
        self.tail_call_count = 0

        # Dispatch table per le operazioni binarie
        self.binary_operators = SaltinoOperators.get_binary_operators()

        # Dispatch table per le operazioni unarie
        self.unary_operators = SaltinoOperators.get_unary_operators()

        # Dispatch table per gli operatori di confronto
        self.comparison_operators = SaltinoOperators.get_comparison_operators()

        # Dispatch table per le operazioni logiche
        self.logical_operators = SaltinoOperators.get_logical_operators()

        # Dispatch table per i frame handlers
        self.frame_handlers = {
            FrameType.FUNCTION_CALL: handlers.execute_function_frame,
            FrameType.BLOCK: handlers.execute_block_frame,
            FrameType.EXPRESSION: handlers.execute_expression_frame,
            FrameType.CONDITION: handlers.execute_condition_frame,
            FrameType.IF_STATEMENT: handlers.execute_if_frame,
            FrameType.ASSIGNMENT: handlers.execute_assignment_frame,
            FrameType.RETURN: handlers.execute_return_frame,
        }

    def _create_new_environment(self, parent: Environment = None) -> Environment:
        """Crea un nuovo ambiente con il parent specificato."""
        return Environment(parent or self.global_env)

    def push_frame(self, frame_type: FrameType, node: ASTNode, environment: Environment):
        """Aggiunge un nuovo frame allo stack di esecuzione con il riferimento al semantic analyzer."""
        frame = ExecutionFrame(
            frame_type, node, environment, self.semantic_analyzer)
        self.execution_stack.append(frame)

        # Traccia la profondità dello stack per l'analisi TCO
        current_depth = len(self.execution_stack)
        if current_depth > self.max_stack_depth:
            self.max_stack_depth = current_depth

        # Conta le chiamate di funzione
        if frame_type == FrameType.FUNCTION_CALL:
            self.function_call_count += 1

        if self.debug_mode:
            print(
                f"[STACK] Pushato frame {frame_type.name}. Profondità attuale: {current_depth}")

        return frame

    def pop_frame(self) -> Optional[ExecutionFrame]:
        """Rimuove e restituisce l'ultimo frame dallo stack."""
        if self.execution_stack:
            return self.execution_stack.pop()
        return None

    def current_frame(self) -> Optional[ExecutionFrame]:
        """Restituisce il frame corrente senza rimuoverlo."""
        if self.execution_stack:
            return self.execution_stack[-1]
        return None

    def execute_program(self, program: Program) -> Any:
        """Esegue un programma Saltino in modo iterativo."""
        # L'analisi semantica è già stata eseguita nel parser
        # Quindi possiamo procedere direttamente con l'esecuzione

        # Registra tutte le funzioni nell'ambiente globale
        for function in program.functions:
            self.global_env.define_function(function.name, function)

        # Cerca la funzione main e la esegue
        try:
            main_function = self.global_env.get_function('main')
        except SaltinoRuntimeError:
            raise SaltinoRuntimeError("No main function found")

        # Se main ha parametri, chiede all'utente di inserirli
        args = get_main_arguments(main_function)
        return self.call_function(main_function, args)

    def call_function(self, function: Function, arguments: List[Any]) -> Any:
        """Inizia la chiamata di una funzione pushando un frame sullo stack."""
        if len(arguments) != len(function.parameters):
            raise SaltinoRuntimeError(
                f"Function '{function.name}' expects {len(function.parameters)} arguments, "
                f"got {len(arguments)}"
            )

        # Crea un nuovo ambiente per la funzione
        function_env = self._create_new_environment(self.global_env)

        # Binding dei parametri usando i nomi univoci
        for param, arg in zip(function.parameters, arguments):
            # Ottieni il nome univoco del parametro dalla symbol table
            # Cerca nelle informazioni del nodo della funzione
            function_scope = self.semantic_analyzer.get_node_info(
                function, 'scope')
            if function_scope:
                try:
                    param_info = function_scope.lookup(param)
                    unique_param_name = param_info.unique_name
                    function_env.define_variable(unique_param_name, arg)
                    if self.debug_mode:
                        print(
                            f"[PARAM] Bound parameter {param} (unique: {unique_param_name}) = {arg}")
                except ValueError:
                    # Fallback al nome originale se non si trova nella symbol table
                    function_env.define_variable(param, arg)
                    if self.debug_mode:
                        print(
                            f"[PARAM] Bound parameter {param} (original name) = {arg}")
            else:
                # Fallback al nome originale se non c'è scope information
                function_env.define_variable(param, arg)
                if self.debug_mode:
                    print(
                        f"[PARAM] Bound parameter {param} (original name, no scope) = {arg}")

        # Pusha il frame della funzione
        frame = self.push_frame(FrameType.FUNCTION_CALL,
                                function, function_env)
        frame.state['function'] = function
        frame.state['body_executed'] = False

        # Inizia l'esecuzione iterativa
        return self.execute()

    def execute(self) -> Any:
        """Loop principale di esecuzione iterativa."""
        while self.execution_stack:
            frame = self.current_frame()

            if frame.completed:
                # Il frame è completato, propaghiamo il risultato
                result = frame.result
                self.pop_frame()

                # Se c'è un frame parent, gli passiamo il risultato
                if self.execution_stack:
                    parent_frame = self.current_frame()
                    self._handle_child_result(parent_frame, result)
                else:
                    # Non ci sono più frame, ritorniamo il risultato finale
                    return result
                continue

            # Elabora il frame corrente usando la dispatch table
            try:
                handler = self.frame_handlers.get(frame.frame_type)
                if handler:
                    handler(frame, self)
                else:
                    raise SaltinoRuntimeError(
                        f"Unknown frame type: {frame.frame_type}")
            except Exception as e:
                # Gestione degli errori - propaga l'errore
                if isinstance(e, SaltinoRuntimeError):
                    raise e
                else:
                    raise SaltinoRuntimeError(f"Internal error: {str(e)}")

        return None

    def _handle_child_result(self, parent_frame: ExecutionFrame, result: Any):
        """Gestisce il risultato di un frame figlio nel frame parent."""
        if parent_frame.frame_type == FrameType.FUNCTION_CALL:
            # Il corpo della funzione è stato eseguito
            parent_frame.state['body_result'] = result
            parent_frame.state['body_executed'] = True
        elif parent_frame.frame_type == FrameType.BLOCK:
            # Una statement del blocco è stata eseguita
            parent_frame.state['statements_results'].append(result)
            parent_frame.state['current_statement_index'] += 1
        elif parent_frame.frame_type == FrameType.EXPRESSION:
            # Gestiamo le chiamate di funzione e le altre espressioni
            if isinstance(parent_frame.node, FunctionCall):
                # Gestiamo le diverse fasi della chiamata di funzione
                current_phase = parent_frame.state.get(
                    'current_phase', 'evaluating_function')

                if current_phase == 'evaluating_function':
                    # La funzione è stata valutata
                    parent_frame.state['function_value'] = result
                    parent_frame.state['function_evaluated'] = True
                elif current_phase == 'evaluating_arguments':
                    # Un argomento è stato valutato
                    parent_frame.state['arguments_evaluated'].append(result)
                    parent_frame.state['current_arg_index'] += 1
                elif current_phase == 'executing_function':
                    # Il risultato della chiamata di funzione
                    parent_frame.result = result
                    parent_frame.completed = True
            else:
                # Un operando è stato valutato per un'altra espressione
                parent_frame.state['operands_evaluated'].append(result)
                parent_frame.state['current_operand_index'] += 1
        elif parent_frame.frame_type == FrameType.CONDITION:
            # Un operando della condizione è stato valutato
            if isinstance(parent_frame.node, FunctionCall):
                # Caso speciale: chiamata di funzione usata come condizione
                current_phase = parent_frame.state.get(
                    'current_phase', 'evaluating_function')

                if current_phase == 'evaluating_function':
                    # La funzione è stata valutata
                    parent_frame.state['function_value'] = result
                    parent_frame.state['function_evaluated'] = True
                elif current_phase == 'evaluating_arguments':
                    # Un argomento è stato valutato
                    parent_frame.state['arguments_evaluated'].append(result)
                    parent_frame.state['current_arg_index'] += 1
                elif current_phase == 'executing_function':
                    # Il risultato della chiamata di funzione usata come condizione
                    parent_frame.state['function_result'] = result
            else:
                # Operando normale di una condizione
                parent_frame.state['operands_evaluated'].append(result)
                parent_frame.state['current_operand_index'] += 1
        elif parent_frame.frame_type == FrameType.IF_STATEMENT:
            if not parent_frame.state['condition_evaluated']:
                # La condizione è stata valutata
                parent_frame.state['condition_result'] = result
                parent_frame.state['condition_evaluated'] = True
            else:
                # Il ramo è stato eseguito
                parent_frame.state['branch_result'] = result
                parent_frame.state['branch_executed'] = True
        elif parent_frame.frame_type == FrameType.ASSIGNMENT:
            # Il valore dell'assegnamento è stato valutato
            parent_frame.state['value'] = result
            parent_frame.state['value_evaluated'] = True
        elif parent_frame.frame_type == FrameType.RETURN:
            # Supporto TCO: gestisce le fasi di valutazione delle tail call
            tco_phase = parent_frame.state.get('tco_phase')
            if tco_phase == 'eval_callee':
                # Memorizza l'oggetto funzione valutato
                parent_frame.state['tail_call_function_value'] = result
                if self.debug_mode:
                    print(f"[TCO] Callee evaluato: {result}")
                # Avanza alla fase di valutazione degli argomenti
                parent_frame.state['tco_phase'] = 'eval_args'
            elif tco_phase == 'eval_args':
                # Siamo nella fase di valutazione degli argomenti TCO
                args = parent_frame.node.value.arguments
                idx = parent_frame.state['tail_call_current_arg_index']
                parent_frame.state['tail_call_evaluated_args'].append(result)
                parent_frame.state['tail_call_current_arg_index'] += 1
                if self.debug_mode:
                    print(f"[TCO] Argument {idx} evaluated: {result}")
                # If all arguments are evaluated, move to next phase
                if parent_frame.state['tail_call_current_arg_index'] >= len(args):
                    parent_frame.state['tco_phase'] = 'ready_to_tailcall'
            else:
                # Standard return value evaluation
                parent_frame.state['return_value'] = result
                parent_frame.state['value_evaluated'] = True

    def print_execution_stats(self):
        """Stampa le statistiche di esecuzione per l'analisi TCO."""
        if self.debug_mode:
            print(f"\n[STATS] Statistiche di Esecuzione:")
            print(
                f"[STATS] Profondità massima dello stack: {self.max_stack_depth}")
            print(
                f"[STATS] Chiamate di funzione totali: {self.function_call_count}")
            print(f"[STATS] Tail call ottimizzate: {self.tail_call_count}")
            if self.function_call_count > 0:
                optimization_ratio = (
                    self.tail_call_count / self.function_call_count) * 100
                print(
                    f"[STATS] Rapporto di ottimizzazione TCO: {optimization_ratio:.1f}%")
