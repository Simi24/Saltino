#!/usr/bin/env python3
"""
Interprete Iterativo per il linguaggio Saltino.

Questo interprete utilizza uno stack di frame di esecuzione per eliminare
la ricorsione dalle chiamate di funzioni e fornisce esecuzione iterativa
del codice rappresentato dall'AST.
"""

from Grammatica.SaltinoParser import SaltinoParser
from Grammatica.SaltinoLexer import SaltinoLexer
from AST.ASTVisitor import build_ast
from AST.ASTNodes import *
from AST.semantic_analyzer import SemanticAnalyzer
from AST.ASTsymbol_table import SymbolTable, SymbolInfo, SymbolKind
from antlr4 import InputStream, CommonTokenStream
from custom_error_listener import create_error_listener, SaltinoSyntaxError
from parser_errors import ErrorCollector, ErrorSeverity, SaltinoParseError
from typing import Any, Dict, List, Optional, Union
import sys
import os
from dataclasses import dataclass, field
from enum import Enum
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def parse_saltino(input_text: str, raise_on_error: bool = True) -> tuple[Optional[Program], ErrorCollector]:
    """
    Parsa il codice sorgente Saltino utilizzando il custom error listener.

    Args:
        input_text: Il codice sorgente da parsare
        raise_on_error: Se True, solleva eccezioni in caso di errori di parsing

    Returns:
        Tupla contenente (AST, ErrorCollector)

    Raises:
        SaltinoParseError: Se ci sono errori di parsing e raise_on_error è True
    """
    # Crea un collettore di errori
    error_collector = ErrorCollector()

    try:
        # Crea lo stream di input
        input_stream = InputStream(input_text)

        # Crea il lexer con custom error listener
        lexer = SaltinoLexer(input_stream)
        lexer_error_listener = create_error_listener()
        lexer_error_listener.error_collector = error_collector
        lexer.removeErrorListeners()  # Rimuovi i listener di default
        lexer.addErrorListener(lexer_error_listener)

        # Crea lo stream di token
        token_stream = CommonTokenStream(lexer)

        # Crea il parser con custom error listener
        parser = SaltinoParser(token_stream)
        parser_error_listener = create_error_listener()
        parser_error_listener.error_collector = error_collector
        parser.removeErrorListeners()  # Rimuovi i listener di default
        parser.addErrorListener(parser_error_listener)

        # Parsa il programma
        tree = parser.programma()

        # Controlla se ci sono stati errori di parsing
        if error_collector.has_errors():
            if raise_on_error:
                # Genera un report degli errori e solleva un'eccezione
                error_report = error_collector.get_error_report()
                raise error_report.errors[0]  # Solleva il primo errore
            else:
                # In modalità non-raising, ritorna None per l'AST
                return None, error_collector

        # Costruisci l'AST se non ci sono errori
        ast = build_ast(tree)

        # Se ci sono stati warning ma non errori, li includiamo nel report
        if error_collector.has_warnings():
            print("Warning durante il parsing:")
            for warning in error_collector.get_warnings():
                print(f"  {warning}")

        return ast, error_collector

    except Exception as e:
        # Se è già un'eccezione Saltino personalizzata, rilanciala
        if hasattr(e, 'position') and hasattr(e, 'message'):
            if raise_on_error:
                raise e
            else:
                error_collector.add_error(e, ErrorSeverity.FATAL)
                return None, error_collector
        else:
            # Altrimenti wrappala in un'eccezione generica
            parse_error = SaltinoParseError(
                f"Errore critico durante il parsing: {str(e)}")
            if raise_on_error:
                raise parse_error
            else:
                error_collector.add_error(parse_error, ErrorSeverity.FATAL)
                return None, error_collector


class SaltinoRuntimeError(Exception):
    """Eccezione per errori di runtime del linguaggio Saltino."""

    def __init__(self, message: str, position: Optional[SourcePosition] = None):
        self.message = message
        self.position = position
        super().__init__(self._format_message())

    def _format_message(self):
        if self.position:
            return f"Runtime Error at {self.position}: {self.message}"
        return f"Runtime Error: {self.message}"


class FrameType(Enum):
    """Tipi di frame nello stack di esecuzione."""
    FUNCTION_CALL = "function_call"
    BLOCK = "block"
    EXPRESSION = "expression"
    CONDITION = "condition"
    IF_STATEMENT = "if_statement"
    ASSIGNMENT = "assignment"
    RETURN = "return"


@dataclass
class ExecutionFrame:
    """Frame di esecuzione contenente lo stato di un'operazione."""
    frame_type: FrameType
    node: ASTNode
    environment: 'Environment'
    # Riferimento all'analizzatore semantico
    semantic_analyzer: Optional['SemanticAnalyzer'] = None
    state: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    completed: bool = False

    def __post_init__(self):
        # Inizializza lo stato specifico per tipo di frame
        if self.frame_type == FrameType.FUNCTION_CALL:
            self.state.setdefault('arguments_evaluated', [])
            self.state.setdefault('current_arg_index', 0)
            self.state.setdefault('function_resolved', False)
            self.state.setdefault('body_executed', False)
        elif self.frame_type == FrameType.BLOCK:
            self.state.setdefault('current_statement_index', 0)
            self.state.setdefault('statements_results', [])
        elif self.frame_type == FrameType.EXPRESSION:
            self.state.setdefault('operands_evaluated', [])
            self.state.setdefault('current_operand_index', 0)
            # Inizializzazioni specifiche per chiamate di funzione in espressioni
            if hasattr(self, 'node') and isinstance(self.node, FunctionCall):
                self.state.setdefault('function_evaluated', False)
                self.state.setdefault('function_resolved', False)
                self.state.setdefault('function_called', False)
                self.state.setdefault('current_phase', 'evaluating_function')
                self.state.setdefault('arguments_evaluated', [])
                self.state.setdefault('current_arg_index', 0)
        elif self.frame_type == FrameType.CONDITION:
            self.state.setdefault('operands_evaluated', [])
            self.state.setdefault('current_operand_index', 0)
            # Inizializzazioni specifiche per chiamate di funzione in condizioni
            if hasattr(self, 'node') and isinstance(self.node, FunctionCall):
                self.state.setdefault('function_evaluated', False)
                self.state.setdefault('function_resolved', False)
                self.state.setdefault('function_called', False)
                self.state.setdefault('current_phase', 'evaluating_function')
                self.state.setdefault('arguments_evaluated', [])
                self.state.setdefault('current_arg_index', 0)
        elif self.frame_type == FrameType.IF_STATEMENT:
            self.state.setdefault('condition_evaluated', False)
            self.state.setdefault('condition_result', None)
            self.state.setdefault('branch_executed', False)


class Environment:
    """
    Ambiente per le variabili e le funzioni con supporto per nomi semantici univoci.

    Utilizza i nomi univoci generati dal SemanticAnalyzer per evitare conflitti
    e gestire correttamente gli scope durante l'esecuzione iterativa.
    """

    def __init__(self, parent: Optional['Environment'] = None, scope_name: str = "env"):
        self.parent = parent
        self.scope_name = scope_name
        # Usa nomi univoci dalla symbol table invece dei nomi originali
        # chiave: unique_name, valore: valore runtime
        self.variables: Dict[str, Any] = {}
        # chiave: nome funzione, valore: AST funzione
        self.functions: Dict[str, Function] = {}

    def get_unique_name(self, node: ASTNode, semantic_analyzer: SemanticAnalyzer) -> str:
        """
        Ottiene il nome univoco per un nodo dall'analizzatore semantico.
        Usato per identificatori e assegnamenti.
        """
        if isinstance(node, Identifier):
            # Per gli identificatori, cerca nella symbol table
            scope = semantic_analyzer.get_node_info(node, 'scope')
            if scope:
                try:
                    symbol_info = scope.lookup(node.name)
                    return symbol_info.unique_name
                except ValueError:
                    raise SaltinoRuntimeError(
                        f"Undefined variable: {node.name}")
            else:
                raise SaltinoRuntimeError(
                    f"No scope information for identifier: {node.name}")
        elif isinstance(node, Assignment):
            # Per gli assegnamenti, cerca le informazioni della variabile
            var_info = semantic_analyzer.get_node_info(node, 'variable_info')
            if var_info:
                return var_info.unique_name
            else:
                raise SaltinoRuntimeError(
                    f"No variable info for assignment: {node.variable}")
        else:
            raise SaltinoRuntimeError(
                f"Cannot get unique name for node type: {type(node)}")

    def define_variable(self, unique_name: str, value: Any):
        """Definisce una variabile usando il nome univoco."""
        self.variables[unique_name] = value

    def get_variable(self, unique_name: str) -> Any:
        """Ottiene il valore di una variabile usando il nome univoco."""
        if unique_name in self.variables:
            return self.variables[unique_name]
        elif self.parent:
            return self.parent.get_variable(unique_name)
        else:
            raise SaltinoRuntimeError(
                f"Undefined variable with unique name: {unique_name}")

    def set_variable(self, unique_name: str, value: Any):
        """Imposta il valore di una variabile esistente usando il nome univoco."""
        if unique_name in self.variables:
            self.variables[unique_name] = value
        elif self.parent:
            self.parent.set_variable(unique_name, value)
        else:
            # Se la variabile non esiste, la creiamo nell'ambiente corrente
            self.variables[unique_name] = value

    def define_function(self, name: str, function: Function):
        """Definisce una funzione nell'ambiente corrente."""
        self.functions[name] = function

    def get_function(self, name: str) -> Function:
        """Ottiene una funzione per nome."""
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        else:
            raise SaltinoRuntimeError(f"Undefined function: {name}")


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

        # Dispatch table per le operazioni binarie
        self.binary_operators = {
            '+': lambda x, y: self._arithmetic_op(x, y, lambda a, b: a + b),
            '-': lambda x, y: self._arithmetic_op(x, y, lambda a, b: a - b),
            '*': lambda x, y: self._arithmetic_op(x, y, lambda a, b: a * b),
            '/': lambda x, y: self._safe_divide(x, y),
            '%': lambda x, y: self._arithmetic_op(x, y, lambda a, b: a % b),
            '^': lambda x, y: self._arithmetic_op(x, y, lambda a, b: a ** b),
            '::': lambda x, y: self._cons(x, y),
        }

        # Dispatch table per le operazioni unarie
        self.unary_operators = {
            '+': lambda x: self._unary_arithmetic_op(x, lambda a: +a),
            '-': lambda x: self._unary_arithmetic_op(x, lambda a: -a),
            'head': lambda x: self._head(x),
            'tail': lambda x: self._tail(x),
        }

        # Dispatch table per gli operatori di confronto
        self.comparison_operators = {
            '==': lambda x, y: self._equality_comparison(x, y),
            '!=': lambda x, y: self._comparison_op(x, y, lambda a, b: a != b),
            '<': lambda x, y: self._comparison_op(x, y, lambda a, b: a < b),
            '<=': lambda x, y: self._comparison_op(x, y, lambda a, b: a <= b),
            '>': lambda x, y: self._comparison_op(x, y, lambda a, b: a > b),
            '>=': lambda x, y: self._comparison_op(x, y, lambda a, b: a >= b),
        }

        # Dispatch table per le operazioni logiche
        self.logical_operators = {
            'and': lambda x, y: self._logical_op(x, y, lambda a, b: a and b),
            'or': lambda x, y: self._logical_op(x, y, lambda a, b: a or b),
        }

    def _safe_divide(self, x: Union[int, float], y: Union[int, float]) -> Union[int, float]:
        """Divisione sicura che controlla la divisione per zero."""
        # Controllo di tipo: operatori aritmetici possono operare solo tra interi
        if type(x) is not int or type(y) is not int:
            raise SaltinoRuntimeError(
                f"Arithmetic operators can only operate on integers, got {type(x).__name__} and {type(y).__name__}")
        if y == 0:
            raise SaltinoRuntimeError("Division by zero")
        return x // y  # Divisione intera per mantenere il tipo intero

    def _cons(self, head: Any, tail: List[Any]) -> List[Any]:
        """Operatore cons (::) che aggiunge un elemento all'inizio di una lista."""
        # Controllo di tipo: :: può operare solo tra un intero e una lista di interi
        if type(head) is not int:
            raise SaltinoRuntimeError(
                f"Cons operator expects an integer as first argument, got {type(head).__name__}")
        if not isinstance(tail, list):
            raise SaltinoRuntimeError(
                f"Cons operator expects a list as second argument, got {type(tail).__name__}")
        # Verifica che tutti gli elementi della lista siano interi
        for i, item in enumerate(tail):
            if type(item) is not int:
                raise SaltinoRuntimeError(
                    f"Cons operator expects a list of integers, but element at index {i} is {type(item).__name__}")
        return [head] + tail

    def _head(self, lst: List[Any]) -> Any:
        """Restituisce il primo elemento di una lista."""
        if not isinstance(lst, list):
            raise SaltinoRuntimeError(
                f"Head operator expects a list, got {type(lst)}")
        if len(lst) == 0:
            raise SaltinoRuntimeError("Head of empty list")
        return lst[0]

    def _tail(self, lst: List[Any]) -> List[Any]:
        """Restituisce la coda di una lista (tutti gli elementi tranne il primo)."""
        if not isinstance(lst, list):
            raise SaltinoRuntimeError(
                f"Tail operator expects a list, got {type(lst)}")
        if len(lst) == 0:
            raise SaltinoRuntimeError("Tail of empty list")
        return lst[1:]

    def _create_new_environment(self, parent: Environment = None) -> Environment:
        """Crea un nuovo ambiente con il parent specificato."""
        return Environment(parent or self.global_env)

    def _get_main_arguments(self, main_function: Function) -> List[Any]:
        """
        Ottiene gli argomenti per la funzione main dall'utente.
        Se main non ha parametri, restituisce una lista vuota.
        Se main ha parametri, chiede all'utente di inserirli.
        """
        if not main_function.parameters:
            return []

        print(
            f"The main function requires {len(main_function.parameters)} parameter(s): {', '.join(main_function.parameters)}")
        print("Please enter the values:")

        args = []
        for param in main_function.parameters:
            while True:
                try:
                    user_input = input(f"  {param}: ").strip()

                    # Prova a parsare come intero
                    if user_input.isdigit() or (user_input.startswith('-') and user_input[1:].isdigit()):
                        args.append(int(user_input))
                        break

                    # Prova a parsare come booleano
                    elif user_input.lower() in ['true', 'false']:
                        args.append(user_input.lower() == 'true')
                        break

                    # Prova a parsare come lista vuota
                    elif user_input == '[]':
                        args.append([])
                        break

                    else:
                        print(
                            f"    Invalid input. Please enter an integer, 'true', 'false', or '[]'")

                except KeyboardInterrupt:
                    print("\nExecution cancelled by user.")
                    sys.exit(0)
                except EOFError:
                    print("\nNo input provided. Exiting.")
                    sys.exit(0)

        return args

    def push_frame(self, frame_type: FrameType, node: ASTNode, environment: Environment):
        """Aggiunge un nuovo frame allo stack di esecuzione con il riferimento al semantic analyzer."""
        frame = ExecutionFrame(
            frame_type, node, environment, self.semantic_analyzer)
        self.execution_stack.append(frame)
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
        """Esegue un programma Saltino in modo iterativo con analisi semantica."""
        # Primo passo: esegue l'analisi semantica
        self.semantic_analyzer = SemanticAnalyzer(debug_mode=self.debug_mode)
        analysis_success = self.semantic_analyzer.analyze(program)

        # Se l'analisi semantica fallisce, interrompi l'esecuzione
        if not analysis_success:
            return None

        # self.semantic_analyzer.print_symbol_tables()

        # Secondo passo: registra tutte le funzioni nell'ambiente globale
        for function in program.functions:
            self.global_env.define_function(function.name, function)

        # Terzo passo: cerca la funzione main e la esegue
        try:
            main_function = self.global_env.get_function('main')
        except SaltinoRuntimeError:
            raise SaltinoRuntimeError("No main function found")

        # Se main ha parametri, chiede all'utente di inserirli
        args = self._get_main_arguments(main_function)
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

        # Binding dei parametri usando i nomi univoci dalla symbol table
        # Ottieni lo scope della funzione dall'analizzatore semantico
        function_scope = self.semantic_analyzer.get_node_info(
            function, 'scope')
        if function_scope:
            for param, arg in zip(function.parameters, arguments):
                try:
                    # Cerca il parametro nella symbol table dello scope della funzione
                    param_info = function_scope.lookup_local(param)
                    if param_info and param_info.kind == SymbolKind.PARAMETER:
                        # Usa il nome univoco del parametro
                        function_env.define_variable(
                            param_info.unique_name, arg)
                    else:
                        raise SaltinoRuntimeError(
                            f"Parameter '{param}' not found in function scope")
                except ValueError:
                    raise SaltinoRuntimeError(
                        f"Parameter '{param}' not found in symbol table")
        else:
            raise SaltinoRuntimeError(
                f"No scope information for function '{function.name}'")

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

            # Elabora il frame corrente basandosi sul suo tipo
            try:
                if frame.frame_type == FrameType.FUNCTION_CALL:
                    self._execute_function_frame(frame)
                elif frame.frame_type == FrameType.BLOCK:
                    self._execute_block_frame(frame)
                elif frame.frame_type == FrameType.EXPRESSION:
                    self._execute_expression_frame(frame)
                elif frame.frame_type == FrameType.CONDITION:
                    self._execute_condition_frame(frame)
                elif frame.frame_type == FrameType.IF_STATEMENT:
                    self._execute_if_frame(frame)
                elif frame.frame_type == FrameType.ASSIGNMENT:
                    self._execute_assignment_frame(frame)
                elif frame.frame_type == FrameType.RETURN:
                    self._execute_return_frame(frame)
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
            # Il valore del return è stato valutato
            parent_frame.state['return_value'] = result
            parent_frame.state['value_evaluated'] = True

    def _execute_function_frame(self, frame: ExecutionFrame):
        """Esegue un frame di chiamata di funzione."""
        function = frame.state['function']

        if not frame.state['body_executed']:
            # Eseguiamo il corpo della funzione
            self.push_frame(FrameType.BLOCK, function.body, frame.environment)
        else:
            # Il corpo è stato eseguito, completiamo il frame
            result = frame.state.get('body_result')
            frame.result = result
            frame.completed = True

    def _execute_block_frame(self, frame: ExecutionFrame):
        """Esegue un frame di blocco."""
        block = frame.node
        statements = block.statements
        current_index = frame.state['current_statement_index']

        if current_index < len(statements):
            # Eseguiamo la prossima statement
            stmt = statements[current_index]
            self._push_statement_frame(stmt, frame.environment)
        else:
            # Tutte le statement sono state eseguite
            results = frame.state['statements_results']
            # Il risultato del blocco è l'ultimo valore calcolato
            frame.result = results[-1] if results else None
            frame.completed = True

    def _push_statement_frame(self, stmt: ASTNode, environment: Environment):
        """Pusha il frame appropriato per una statement."""
        if isinstance(stmt, Assignment):
            self.push_frame(FrameType.ASSIGNMENT, stmt, environment)
        elif isinstance(stmt, IfStatement):
            self.push_frame(FrameType.IF_STATEMENT, stmt, environment)
        elif isinstance(stmt, ReturnStatement):
            self.push_frame(FrameType.RETURN, stmt, environment)
        elif isinstance(stmt, Block):
            self.push_frame(FrameType.BLOCK, stmt, environment)
        else:
            # È un'espressione o condizione
            if self._is_condition_node(stmt):
                self.push_frame(FrameType.CONDITION, stmt, environment)
            else:
                self.push_frame(FrameType.EXPRESSION, stmt, environment)

    def _is_condition_node(self, node: ASTNode) -> bool:
        """Determina se un nodo è una condizione."""
        return isinstance(node, (BooleanLiteral, BinaryCondition,
                                 UnaryCondition, ComparisonCondition))

    def _execute_expression_frame(self, frame: ExecutionFrame):
        """Esegue un frame di espressione."""
        node = frame.node

        # Gestione dei diversi tipi di espressione
        if isinstance(node, IntegerLiteral):
            frame.result = node.value
            frame.completed = True
        elif isinstance(node, BooleanLiteral):
            frame.result = node.value
            frame.completed = True
        elif isinstance(node, Identifier):
            try:
                # Usa il nome univoco dalla symbol table per accedere alla variabile
                unique_name = frame.environment.get_unique_name(
                    node, frame.semantic_analyzer)
                frame.result = frame.environment.get_variable(unique_name)
                frame.completed = True
            except SaltinoRuntimeError as e:
                # Se non è una variabile, potrebbe essere una funzione
                try:
                    function = frame.environment.get_function(node.name)
                    frame.result = function
                    frame.completed = True
                except SaltinoRuntimeError:
                    # Controlla se è un caso di variable shadowing (UnboundLocalError)
                    if "unique name" in str(e):
                        raise SaltinoRuntimeError(
                            f"UnboundLocalError: cannot access local variable '{node.name}' "
                            f"where it is not associated with a value. "
                            f"(Variable '{node.name}' is assigned in this scope, making it local, "
                            f"but it's used before assignment)")
                    else:
                        raise SaltinoRuntimeError(
                            f"Undefined variable or function: {node.name}")
        elif isinstance(node, EmptyList):
            frame.result = []
            frame.completed = True
        elif isinstance(node, BinaryExpression):
            self._execute_binary_expression(frame)
        elif isinstance(node, UnaryExpression):
            self._execute_unary_expression(frame)
        elif isinstance(node, FunctionCall):
            self._execute_function_call_expression(frame)
        else:
            raise SaltinoRuntimeError(f"Unknown expression type: {type(node)}")

    def _execute_binary_expression(self, frame: ExecutionFrame):
        """Esegue un'espressione binaria."""
        expr = frame.node
        operands_evaluated = frame.state['operands_evaluated']
        current_index = frame.state['current_operand_index']

        if current_index == 0:
            # Valutiamo l'operando sinistro
            if self._is_condition_node(expr.left):
                self.push_frame(FrameType.CONDITION,
                                expr.left, frame.environment)
            else:
                self.push_frame(FrameType.EXPRESSION,
                                expr.left, frame.environment)
        elif current_index == 1:
            # Valutiamo l'operando destro
            if self._is_condition_node(expr.right):
                self.push_frame(FrameType.CONDITION,
                                expr.right, frame.environment)
            else:
                self.push_frame(FrameType.EXPRESSION,
                                expr.right, frame.environment)
        else:
            # Entrambi gli operandi sono stati valutati
            left_value = operands_evaluated[0]
            right_value = operands_evaluated[1]

            if expr.operator in self.binary_operators:
                frame.result = self.binary_operators[expr.operator](
                    left_value, right_value)
            else:
                raise SaltinoRuntimeError(
                    f"Unknown binary operator: {expr.operator}")

            frame.completed = True

    def _execute_unary_expression(self, frame: ExecutionFrame):
        """Esegue un'espressione unaria."""
        expr = frame.node
        operands_evaluated = frame.state['operands_evaluated']
        current_index = frame.state['current_operand_index']

        if current_index == 0:
            # Valutiamo l'operando
            if self._is_condition_node(expr.operand):
                self.push_frame(FrameType.CONDITION,
                                expr.operand, frame.environment)
            else:
                self.push_frame(FrameType.EXPRESSION,
                                expr.operand, frame.environment)
        else:
            # L'operando è stato valutato
            operand_value = operands_evaluated[0]

            if expr.operator in self.unary_operators:
                frame.result = self.unary_operators[expr.operator](
                    operand_value)
            else:
                raise SaltinoRuntimeError(
                    f"Unknown unary operator: {expr.operator}")

            frame.completed = True

    def _execute_function_call_expression(self, frame: ExecutionFrame):
        """Esegue una chiamata di funzione all'interno di un'espressione."""
        call = frame.node

        if not frame.state.get('function_evaluated', False):
            # Prima valutiamo l'espressione del callee (potrebbe essere una variabile che contiene una funzione)
            if self._is_condition_node(call.function):
                self.push_frame(FrameType.CONDITION,
                                call.function, frame.environment)
            else:
                self.push_frame(FrameType.EXPRESSION,
                                call.function, frame.environment)
            frame.state['current_phase'] = 'evaluating_function'
            frame.state['arguments_to_evaluate'] = call.arguments[:]
            frame.state['arguments_evaluated'] = []
            frame.state['current_arg_index'] = 0
            return

        if not frame.state.get('function_resolved', False):
            # Il callee è stato valutato, ora determiniamo se è una funzione valida
            function_value = frame.state['function_value']

            # Verifichiamo se è un oggetto Function
            if isinstance(function_value, Function):
                frame.state['function'] = function_value
                frame.state['function_resolved'] = True
            else:
                raise SaltinoRuntimeError(
                    f"Cannot call non-function value of type {type(function_value).__name__}"
                )

        # Valutiamo gli argomenti
        args_evaluated = frame.state['arguments_evaluated']
        current_index = frame.state['current_arg_index']
        args_to_evaluate = frame.state['arguments_to_evaluate']

        if current_index < len(args_to_evaluate):
            # Valutiamo il prossimo argomento
            arg = args_to_evaluate[current_index]
            if self._is_condition_node(arg):
                self.push_frame(FrameType.CONDITION, arg, frame.environment)
            else:
                self.push_frame(FrameType.EXPRESSION, arg, frame.environment)
            frame.state['current_phase'] = 'evaluating_arguments'
        elif not frame.state.get('function_called', False):
            # Tutti gli argomenti sono stati valutati, chiamiamo la funzione
            function = frame.state['function']

            # Verifichiamo il numero di argomenti
            if len(args_evaluated) != len(function.parameters):
                raise SaltinoRuntimeError(
                    f"Function '{function.name}' expects {len(function.parameters)} arguments, "
                    f"got {len(args_evaluated)}"
                )

            # Creiamo un nuovo ambiente per la funzione
            function_env = self._create_new_environment(self.global_env)

            # Binding dei parametri usando i nomi univoci dalla symbol table
            function_scope = self.semantic_analyzer.get_node_info(
                function, 'scope')
            if function_scope:
                for param, arg in zip(function.parameters, args_evaluated):
                    try:
                        param_info = function_scope.lookup_local(param)
                        if param_info and param_info.kind == SymbolKind.PARAMETER:
                            function_env.define_variable(
                                param_info.unique_name, arg)
                        else:
                            raise SaltinoRuntimeError(
                                f"Parameter '{param}' not found in function scope")
                    except ValueError:
                        raise SaltinoRuntimeError(
                            f"Parameter '{param}' not found in symbol table")
            else:
                raise SaltinoRuntimeError(
                    f"No scope information for function '{function.name}'")

            # Eseguiamo la funzione
            func_frame = self.push_frame(
                FrameType.FUNCTION_CALL, function, function_env)
            func_frame.state['function'] = function
            func_frame.state['body_executed'] = False

            frame.state['function_called'] = True
            frame.state['current_phase'] = 'executing_function'
        # Se arriviamo qui e la funzione è stata chiamata, il risultato sarà gestito da _handle_child_result

    def _execute_condition_frame(self, frame: ExecutionFrame):
        """Esegue un frame di condizione."""
        node = frame.node

        if isinstance(node, BooleanLiteral):
            frame.result = node.value
            frame.completed = True
        elif isinstance(node, Identifier):
            try:
                # Usa il nome univoco dalla symbol table per accedere alla variabile
                unique_name = frame.environment.get_unique_name(
                    node, frame.semantic_analyzer)
                value = frame.environment.get_variable(unique_name)
                # Verifica che il valore sia un booleano
                if type(value) is not bool:
                    raise SaltinoRuntimeError(
                        f"Variable '{node.name}' used in condition must be boolean, got {type(value).__name__}")
                frame.result = value
                frame.completed = True
            except SaltinoRuntimeError as e:
                raise SaltinoRuntimeError(
                    f"Error accessing variable '{node.name}': {e.message}")
        elif isinstance(node, BinaryCondition):
            self._execute_binary_condition(frame)
        elif isinstance(node, UnaryCondition):
            self._execute_unary_condition(frame)
        elif isinstance(node, ComparisonCondition):
            self._execute_comparison_condition(frame)
        elif isinstance(node, FunctionCall):
            # Chiamata di funzione usata come condizione - deve restituire un booleano
            self._execute_function_call_in_condition(frame)
        else:
            raise SaltinoRuntimeError(f"Unknown condition type: {type(node)}")

    def _execute_binary_condition(self, frame: ExecutionFrame):
        """Esegue una condizione binaria."""
        condition = frame.node
        operands_evaluated = frame.state['operands_evaluated']
        current_index = frame.state['current_operand_index']

        if current_index == 0:
            # Valutiamo l'operando sinistro
            self.push_frame(FrameType.CONDITION,
                            condition.left, frame.environment)
        elif current_index == 1:
            # Short-circuit evaluation per and e or
            left_value = operands_evaluated[0]

            # Controllo di tipo per il primo operando
            if type(left_value) is not bool:
                raise SaltinoRuntimeError(
                    f"Logical operators can only operate on boolean values, got {type(left_value).__name__}")

            if condition.operator == 'and' and not left_value:
                frame.result = False
                frame.completed = True
                return
            elif condition.operator == 'or' and left_value:
                frame.result = True
                frame.completed = True
                return

            # Valutiamo l'operando destro
            self.push_frame(FrameType.CONDITION,
                            condition.right, frame.environment)
        else:
            # Entrambi gli operandi sono stati valutati
            left_value = operands_evaluated[0]
            right_value = operands_evaluated[1]

            if condition.operator in self.logical_operators:
                frame.result = self.logical_operators[condition.operator](
                    left_value, right_value)
            else:
                raise SaltinoRuntimeError(
                    f"Unknown logical operator: {condition.operator}")

            frame.completed = True

    def _execute_unary_condition(self, frame: ExecutionFrame):
        """Esegue una condizione unaria."""
        condition = frame.node
        operands_evaluated = frame.state['operands_evaluated']
        current_index = frame.state['current_operand_index']

        if current_index == 0:
            # Valutiamo l'operando
            self.push_frame(FrameType.CONDITION,
                            condition.operand, frame.environment)
        else:
            # L'operando è stato valutato
            operand_value = operands_evaluated[0]

            if condition.operator == '!':
                # Controllo di tipo: negazione può operare solo su valori booleani
                if type(operand_value) is not bool:
                    raise SaltinoRuntimeError(
                        f"Logical negation can only operate on boolean values, got {type(operand_value).__name__}")
                frame.result = not operand_value
            else:
                raise SaltinoRuntimeError(
                    f"Unknown unary logical operator: {condition.operator}")

            frame.completed = True

    def _execute_comparison_condition(self, frame: ExecutionFrame):
        """Esegue una condizione di confronto."""
        comparison = frame.node
        operands_evaluated = frame.state['operands_evaluated']
        current_index = frame.state['current_operand_index']

        if current_index == 0:
            # Valutiamo l'operando sinistro
            self.push_frame(FrameType.EXPRESSION,
                            comparison.left, frame.environment)
        elif current_index == 1:
            # Valutiamo l'operando destro
            self.push_frame(FrameType.EXPRESSION,
                            comparison.right, frame.environment)
        else:
            # Entrambi gli operandi sono stati valutati
            left_value = operands_evaluated[0]
            right_value = operands_evaluated[1]

            if comparison.operator in self.comparison_operators:
                frame.result = self.comparison_operators[comparison.operator](
                    left_value, right_value)
            else:
                raise SaltinoRuntimeError(
                    f"Unknown comparison operator: {comparison.operator}")

            frame.completed = True

    def _execute_function_call_in_condition(self, frame: ExecutionFrame):
        """Esegue una chiamata di funzione usata come condizione."""
        call = frame.node

        if not frame.state.get('function_evaluated', False):
            # Prima valutiamo l'espressione del callee
            if self._is_condition_node(call.function):
                self.push_frame(FrameType.CONDITION,
                                call.function, frame.environment)
            else:
                self.push_frame(FrameType.EXPRESSION,
                                call.function, frame.environment)
            frame.state['current_phase'] = 'evaluating_function'
            frame.state['arguments_to_evaluate'] = call.arguments[:]
            frame.state['arguments_evaluated'] = []
            frame.state['current_arg_index'] = 0
            return

        if not frame.state.get('function_resolved', False):
            # Il callee è stato valutato, verifichiamo che sia una funzione
            function_value = frame.state['function_value']

            if isinstance(function_value, Function):
                frame.state['function'] = function_value
                frame.state['function_resolved'] = True
            else:
                raise SaltinoRuntimeError(
                    f"Cannot call non-function value of type {type(function_value).__name__}"
                )

        # Valutiamo gli argomenti
        args_evaluated = frame.state['arguments_evaluated']
        current_index = frame.state['current_arg_index']
        args_to_evaluate = frame.state['arguments_to_evaluate']

        if current_index < len(args_to_evaluate):
            # Valutiamo il prossimo argomento
            arg = args_to_evaluate[current_index]
            if self._is_condition_node(arg):
                self.push_frame(FrameType.CONDITION, arg, frame.environment)
            else:
                self.push_frame(FrameType.EXPRESSION, arg, frame.environment)
            frame.state['current_phase'] = 'evaluating_arguments'
        elif not frame.state.get('function_called', False):
            # Tutti gli argomenti sono stati valutati, chiamiamo la funzione
            function = frame.state['function']

            # Verifichiamo il numero di argomenti
            if len(args_evaluated) != len(function.parameters):
                raise SaltinoRuntimeError(
                    f"Function '{function.name}' expects {len(function.parameters)} arguments, "
                    f"got {len(args_evaluated)}"
                )

            # Creiamo un nuovo ambiente per la funzione
            function_env = self._create_new_environment(self.global_env)

            # Binding dei parametri
            function_scope = self.semantic_analyzer.get_node_info(
                function, 'scope')
            if function_scope:
                for param, arg in zip(function.parameters, args_evaluated):
                    try:
                        param_info = function_scope.lookup_local(param)
                        if param_info and param_info.kind == SymbolKind.PARAMETER:
                            function_env.define_variable(
                                param_info.unique_name, arg)
                        else:
                            raise SaltinoRuntimeError(
                                f"Parameter '{param}' not found in function scope")
                    except ValueError:
                        raise SaltinoRuntimeError(
                            f"Parameter '{param}' not found in symbol table")
            else:
                raise SaltinoRuntimeError(
                    f"No scope information for function '{function.name}'")

            # Eseguiamo la funzione
            func_frame = self.push_frame(
                FrameType.FUNCTION_CALL, function, function_env)
            func_frame.state['function'] = function
            func_frame.state['body_executed'] = False

            frame.state['function_called'] = True
            frame.state['current_phase'] = 'executing_function'
        else:
            # La funzione è stata chiamata, il risultato è stato impostato da _handle_child_result
            result = frame.state.get('function_result')
            # Verifichiamo che il risultato sia un booleano
            if type(result) is not bool:
                raise SaltinoRuntimeError(
                    f"Function used in condition must return boolean, got {type(result).__name__}")
            frame.result = result
            frame.completed = True

    def _execute_if_frame(self, frame: ExecutionFrame):
        """Esegue un frame di statement if."""
        if_stmt = frame.node

        if not frame.state['condition_evaluated']:
            # Valutiamo la condizione
            self.push_frame(FrameType.CONDITION,
                            if_stmt.condition, frame.environment)
        elif not frame.state['branch_executed']:
            # La condizione è stata valutata, eseguiamo il ramo appropriato
            condition_result = frame.state['condition_result']

            if condition_result:
                # Eseguiamo il ramo then
                self.push_frame(FrameType.BLOCK,
                                if_stmt.then_block, frame.environment)
            elif if_stmt.else_block:
                # Eseguiamo il ramo else
                self.push_frame(FrameType.BLOCK,
                                if_stmt.else_block, frame.environment)
            else:
                # Nessun ramo else, completiamo con None
                frame.result = None
                frame.completed = True
        else:
            # Il ramo è stato eseguito
            frame.result = frame.state.get('branch_result')
            frame.completed = True

    def _execute_assignment_frame(self, frame: ExecutionFrame):
        """Esegue un frame di assegnamento usando i nomi univoci dalla symbol table."""
        assignment = frame.node

        if not frame.state.get('value_evaluated', False):
            # Valutiamo il valore da assegnare
            if self._is_condition_node(assignment.value):
                self.push_frame(FrameType.CONDITION,
                                assignment.value, frame.environment)
            else:
                self.push_frame(FrameType.EXPRESSION,
                                assignment.value, frame.environment)
        else:
            # Il valore è stato valutato, eseguiamo l'assegnamento usando il nome univoco
            value = frame.state['value']

            # Ottiene il nome univoco dalla symbol table
            unique_name = frame.environment.get_unique_name(
                assignment, frame.semantic_analyzer)
            frame.environment.set_variable(unique_name, value)

            frame.result = value
            frame.completed = True

    def _execute_return_frame(self, frame: ExecutionFrame):
        """Esegue un frame di return."""
        return_stmt = frame.node

        if not frame.state.get('value_evaluated', False):
            # Valutiamo il valore del return
            if self._is_condition_node(return_stmt.value):
                self.push_frame(FrameType.CONDITION,
                                return_stmt.value, frame.environment)
            else:
                self.push_frame(FrameType.EXPRESSION,
                                return_stmt.value, frame.environment)
        else:
            # Il valore è stato valutato
            return_value = frame.state['return_value']

            # Dobbiamo propagare il return fino al frame della funzione
            # Rimuoviamo tutti i frame fino alla funzione
            while self.execution_stack:
                current = self.pop_frame()
                if current.frame_type == FrameType.FUNCTION_CALL:
                    # Impostiamo il risultato e completiamo la funzione
                    current.result = return_value
                    current.completed = True
                    self.execution_stack.append(current)
                    break

            frame.completed = True

    def _arithmetic_op(self, x: Any, y: Any, operation) -> int:
        """Esegue un'operazione aritmetica con controllo di tipo."""
        # Controllo di tipo: operatori aritmetici possono operare solo tra interi
        # Nota: isinstance(True, int) è True in Python, quindi controlliamo esplicitamente bool
        if type(x) is not int or type(y) is not int:
            raise SaltinoRuntimeError(
                f"Arithmetic operators can only operate on integers, got {type(x).__name__} and {type(y).__name__}")
        return operation(x, y)

    def _unary_arithmetic_op(self, x: Any, operation) -> int:
        """Esegue un'operazione aritmetica unaria con controllo di tipo."""
        # Controllo di tipo: operatori aritmetici possono operare solo su interi
        if type(x) is not int:
            raise SaltinoRuntimeError(
                f"Arithmetic operators can only operate on integers, got {type(x).__name__}")
        return operation(x)

    def _comparison_op(self, x: Any, y: Any, operation) -> bool:
        """Esegue un'operazione di confronto con controllo di tipo."""
        # Controllo di tipo: operatori di confronto (eccetto ==) possono operare solo su interi
        if type(x) is not int or type(y) is not int:
            raise SaltinoRuntimeError(
                f"Comparison operators can only operate on integers, got {type(x).__name__} and {type(y).__name__}")
        return operation(x, y)

    def _equality_comparison(self, x: Any, y: Any) -> bool:
        """Esegue il confronto di uguaglianza con regole speciali."""
        # == può operare su interi o tra liste di interi, dove una deve essere []
        if type(x) is int and type(y) is int:
            return x == y
        elif isinstance(x, list) and isinstance(y, list):
            # Almeno una delle due liste deve essere vuota
            if len(x) == 0 or len(y) == 0:
                # Verifica che entrambe siano liste di interi
                for item in x:
                    if type(item) is not int:
                        raise SaltinoRuntimeError(
                            f"Equality comparison on lists requires lists of integers, but found {type(item).__name__} in first list")
                for item in y:
                    if type(item) is not int:
                        raise SaltinoRuntimeError(
                            f"Equality comparison on lists requires lists of integers, but found {type(item).__name__} in second list")
                return x == y
            else:
                raise SaltinoRuntimeError(
                    "Equality comparison between lists is only allowed when at least one list is empty []")
        else:
            raise SaltinoRuntimeError(
                f"Equality comparison can only operate on integers or lists of integers, got {type(x).__name__} and {type(y).__name__}")

    def _logical_op(self, x: Any, y: Any, operation) -> bool:
        """Esegue un'operazione logica con controllo di tipo."""
        # Controllo di tipo: connettivi logici possono operare solo tra valori booleani
        if type(x) is not bool or type(y) is not bool:
            raise SaltinoRuntimeError(
                f"Logical operators can only operate on boolean values, got {type(x).__name__} and {type(y).__name__}")
        return operation(x, y)


def parse_saltino_interactive(input_text: str) -> Optional[Program]:
    """
    Funzione di parsing interattiva che mostra errori dettagliati.

    Args:
        input_text: Il codice sorgente da parsare

    Returns:
        L'AST del programma o None se ci sono errori
    """
    try:
        ast, error_collector = parse_saltino(input_text, raise_on_error=False)

        if error_collector.has_errors():
            print("❌ Errori di parsing:")
            error_report = error_collector.get_error_report()
            print(error_report.format_report())

            # Mostra suggerimenti di recupero
            from custom_error_listener import SaltinoSyntaxErrorStrategy
            for error in error_report.errors:
                if hasattr(error, 'offending_symbol') or hasattr(error, 'expected_tokens'):
                    suggestions = SaltinoSyntaxErrorStrategy.suggest_recovery(
                        error)
                    if suggestions:
                        print("\n💡 Suggerimenti:")
                        for suggestion in suggestions:
                            print(f"  - {suggestion}")

            return None

        if error_collector.has_warnings():
            print("⚠️  Warning:")
            for warning in error_collector.get_warnings():
                print(f"  {warning}")

        print("✅ Parsing completato con successo")
        return ast

    except Exception as e:
        print(f"❌ Errore critico durante il parsing: {e}")
        return None


def exec_saltino_iterative(filename: str, debug_mode: bool = False) -> Any:
    """Esegue un file Saltino usando l'interprete iterativo con gestione errori personalizzata."""
    try:
        with open(filename, 'r') as file:
            program_text = file.read()

        ast, error_collector = parse_saltino(
            program_text, raise_on_error=False)

        # Controlla se ci sono stati errori di parsing
        if error_collector.has_errors():
            print("❌ Errori di parsing rilevati:")
            error_report = error_collector.get_error_report()
            print(error_report.format_report())

            # Mostra suggerimenti di recupero se disponibili
            for error in error_report.errors:
                if hasattr(error, 'get_recovery_suggestions'):
                    suggestions = error.get_recovery_suggestions()
                    if suggestions:
                        print("\n💡 Suggerimenti per la correzione:")
                        for suggestion in suggestions:
                            print(f"  - {suggestion}")

            raise SaltinoRuntimeError(
                "Impossibile procedere a causa di errori di parsing")

        # Se ci sono solo warning, continua ma li mostra
        if error_collector.has_warnings():
            print("⚠️  Warning durante il parsing:")
            for warning in error_collector.get_warnings():
                print(f"  {warning}")

        if ast is None:
            raise SaltinoRuntimeError("Errore nella costruzione dell'AST")

        # Esecuzione con l'interprete iterativo
        interpreter = IterativeSaltinoInterpreter(debug_mode=debug_mode)
        result = interpreter.execute_program(ast)

        return result

    except FileNotFoundError:
        raise SaltinoRuntimeError(f"File not found: {filename}")
    except Exception as e:
        if isinstance(e, SaltinoRuntimeError):
            raise e
        else:
            raise SaltinoRuntimeError(f"Error executing {filename}: {str(e)}")


if __name__ == "__main__":
    debug_mode = False
    filename = None

    # Parse degli argomenti
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--debug":
            debug_mode = True
        elif not arg.startswith("--"):
            filename = arg

    if filename is None:
        print("Usage: python interpreter.py <saltino_file> [--debug]")
        print("\nOptions:")
        print("  --debug    Enable debug mode with verbose output")
        sys.exit(1)

    try:
        result = exec_saltino_iterative(filename, debug_mode=debug_mode)
        print(f"Program result: {result}")
    except SaltinoRuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        sys.exit(0)
