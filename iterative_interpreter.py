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
from antlr4 import InputStream, CommonTokenStream
from typing import Any, Dict, List, Optional, Union
import sys
import os
from dataclasses import dataclass, field
from enum import Enum
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


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
        elif self.frame_type == FrameType.CONDITION:
            self.state.setdefault('operands_evaluated', [])
            self.state.setdefault('current_operand_index', 0)
        elif self.frame_type == FrameType.IF_STATEMENT:
            self.state.setdefault('condition_evaluated', False)
            self.state.setdefault('condition_result', None)
            self.state.setdefault('branch_executed', False)


class Environment:
    """Ambiente per le variabili e le funzioni."""

    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Function] = {}

    def define_variable(self, name: str, value: Any):
        """Definisce una variabile nell'ambiente corrente."""
        self.variables[name] = value

    def get_variable(self, name: str) -> Any:
        """Ottiene il valore di una variabile."""
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable(name)
        else:
            raise SaltinoRuntimeError(f"Undefined variable: {name}")

    def set_variable(self, name: str, value: Any):
        """Imposta il valore di una variabile esistente."""
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.set_variable(name, value)
        else:
            # Se la variabile non esiste, la creiamo nell'ambiente corrente
            self.variables[name] = value

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
    Interprete Iterativo per il linguaggio Saltino.

    Utilizza uno stack di frame di esecuzione per eliminare la ricorsione
    e gestire l'esecuzione in modo iterativo.
    """

    def __init__(self):
        self.global_env = Environment()
        self.execution_stack: List[ExecutionFrame] = []
        self.result_stack: List[Any] = []

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
            raise SaltinoRuntimeError(f"Arithmetic operators can only operate on integers, got {type(x).__name__} and {type(y).__name__}")
        if y == 0:
            raise SaltinoRuntimeError("Division by zero")
        return x // y  # Divisione intera per mantenere il tipo intero

    def _cons(self, head: Any, tail: List[Any]) -> List[Any]:
        """Operatore cons (::) che aggiunge un elemento all'inizio di una lista."""
        # Controllo di tipo: :: può operare solo tra un intero e una lista di interi
        if type(head) is not int:
            raise SaltinoRuntimeError(f"Cons operator expects an integer as first argument, got {type(head).__name__}")
        if not isinstance(tail, list):
            raise SaltinoRuntimeError(f"Cons operator expects a list as second argument, got {type(tail).__name__}")
        # Verifica che tutti gli elementi della lista siano interi
        for i, item in enumerate(tail):
            if type(item) is not int:
                raise SaltinoRuntimeError(f"Cons operator expects a list of integers, but element at index {i} is {type(item).__name__}")
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
        """Aggiunge un nuovo frame allo stack di esecuzione."""
        frame = ExecutionFrame(frame_type, node, environment)
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
        """Esegue un programma Saltino in modo iterativo."""
        # Prima registra tutte le funzioni
        for function in program.functions:
            self.global_env.define_function(function.name, function)

        # Cerca la funzione main e la esegue
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

        # Binding dei parametri
        for param, arg in zip(function.parameters, arguments):
            function_env.define_variable(param, arg)

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
                # Se stiamo valutando argomenti o abbiamo chiamato la funzione
                if not parent_frame.state.get('function_called', False):
                    # Stiamo valutando un argomento
                    parent_frame.state['arguments_evaluated'].append(result)
                    parent_frame.state['current_arg_index'] += 1
                else:
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
                if not parent_frame.state.get('function_called', False):
                    # Stiamo valutando un argomento
                    parent_frame.state['arguments_evaluated'].append(result)
                    parent_frame.state['current_arg_index'] += 1
                else:
                    # Il risultato della chiamata di funzione
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
                frame.result = frame.environment.get_variable(node.name)
                frame.completed = True
            except SaltinoRuntimeError:
                # Se non è una variabile, potrebbe essere una funzione
                try:
                    function = frame.environment.get_function(node.name)
                    frame.result = function
                    frame.completed = True
                except SaltinoRuntimeError:
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

        if not frame.state.get('function_resolved', False):
            # Risolviamo la funzione
            if isinstance(call.function, Identifier):
                function_name = call.function.name
                # Prima prova a trovare come funzione
                try:
                    function = frame.environment.get_function(function_name)
                    frame.state['function'] = function
                    frame.state['function_resolved'] = True
                    frame.state['arguments_to_evaluate'] = call.arguments[:]
                    frame.state['arguments_evaluated'] = []
                    frame.state['current_arg_index'] = 0
                except SaltinoRuntimeError:
                    # Se non è una funzione, prova come variabile che contiene una funzione
                    try:
                        function_obj = frame.environment.get_variable(
                            function_name)
                        if hasattr(function_obj, 'name') and hasattr(function_obj, 'parameters'):
                            # È un oggetto funzione
                            frame.state['function'] = function_obj
                            frame.state['function_resolved'] = True
                            frame.state['arguments_to_evaluate'] = call.arguments[:]
                            frame.state['arguments_evaluated'] = []
                            frame.state['current_arg_index'] = 0
                        else:
                            raise SaltinoRuntimeError(
                                f"Variable {function_name} is not a function")
                    except SaltinoRuntimeError:
                        raise SaltinoRuntimeError(
                            f"Undefined function: {function_name}")
            else:
                raise SaltinoRuntimeError(
                    "Complex function expressions not supported yet")

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
            for param, arg in zip(function.parameters, args_evaluated):
                function_env.define_variable(param, arg)

            # Eseguiamo la funzione
            func_frame = self.push_frame(
                FrameType.FUNCTION_CALL, function, function_env)
            func_frame.state['function'] = function
            func_frame.state['body_executed'] = False

            frame.state['function_called'] = True
        # Se arriviamo qui e la funzione è stata chiamata, il risultato sarà gestito da _handle_child_result

    def _execute_condition_frame(self, frame: ExecutionFrame):
        """Esegue un frame di condizione."""
        node = frame.node

        if isinstance(node, BooleanLiteral):
            frame.result = node.value
            frame.completed = True
        elif isinstance(node, Identifier):
            try:
                value = frame.environment.get_variable(node.name)
                # Verifica che il valore sia un booleano
                if type(value) is not bool:
                    raise SaltinoRuntimeError(f"Variable '{node.name}' used in condition must be boolean, got {type(value).__name__}")
                frame.result = value
                frame.completed = True
            except SaltinoRuntimeError:
                raise SaltinoRuntimeError(f"Undefined variable: {node.name}")
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
                raise SaltinoRuntimeError(f"Logical operators can only operate on boolean values, got {type(left_value).__name__}")
            
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
                    raise SaltinoRuntimeError(f"Logical negation can only operate on boolean values, got {type(operand_value).__name__}")
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

        if not frame.state.get('function_resolved', False):
            # Risolviamo la funzione
            if isinstance(call.function, Identifier):
                try:
                    function = frame.environment.get_function(call.function.name)
                    frame.state['function'] = function
                    frame.state['function_resolved'] = True
                    frame.state['arguments_to_evaluate'] = call.arguments
                    frame.state['arguments_evaluated'] = []
                    frame.state['current_arg_index'] = 0
                except SaltinoRuntimeError:
                    raise SaltinoRuntimeError(f"Undefined function: {call.function.name}")
            else:
                raise SaltinoRuntimeError(f"Complex function expressions not supported")

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
            for param, arg in zip(function.parameters, args_evaluated):
                function_env.define_variable(param, arg)

            # Eseguiamo la funzione
            func_frame = self.push_frame(FrameType.FUNCTION_CALL, function, function_env)
            func_frame.state['function'] = function
            func_frame.state['body_executed'] = False

            frame.state['function_called'] = True
        else:
            # La funzione è stata chiamata, il risultato è stato impostato da _handle_child_result
            result = frame.state.get('function_result')
            # Verifichiamo che il risultato sia un booleano
            if type(result) is not bool:
                raise SaltinoRuntimeError(f"Function used in condition must return boolean, got {type(result).__name__}")
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
        """Esegue un frame di assegnamento."""
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
            # Il valore è stato valutato, eseguiamo l'assegnamento
            value = frame.state['value']
            frame.environment.set_variable(assignment.variable, value)
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
            raise SaltinoRuntimeError(f"Arithmetic operators can only operate on integers, got {type(x).__name__} and {type(y).__name__}")
        return operation(x, y)

    def _unary_arithmetic_op(self, x: Any, operation) -> int:
        """Esegue un'operazione aritmetica unaria con controllo di tipo."""
        # Controllo di tipo: operatori aritmetici possono operare solo su interi
        if type(x) is not int:
            raise SaltinoRuntimeError(f"Arithmetic operators can only operate on integers, got {type(x).__name__}")
        return operation(x)

    def _comparison_op(self, x: Any, y: Any, operation) -> bool:
        """Esegue un'operazione di confronto con controllo di tipo."""
        # Controllo di tipo: operatori di confronto (eccetto ==) possono operare solo su interi
        if type(x) is not int or type(y) is not int:
            raise SaltinoRuntimeError(f"Comparison operators can only operate on integers, got {type(x).__name__} and {type(y).__name__}")
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
                        raise SaltinoRuntimeError(f"Equality comparison on lists requires lists of integers, but found {type(item).__name__} in first list")
                for item in y:
                    if type(item) is not int:
                        raise SaltinoRuntimeError(f"Equality comparison on lists requires lists of integers, but found {type(item).__name__} in second list")
                return x == y
            else:
                raise SaltinoRuntimeError("Equality comparison between lists is only allowed when at least one list is empty []")
        else:
            raise SaltinoRuntimeError(f"Equality comparison can only operate on integers or lists of integers, got {type(x).__name__} and {type(y).__name__}")

    def _logical_op(self, x: Any, y: Any, operation) -> bool:
        """Esegue un'operazione logica con controllo di tipo."""
        # Controllo di tipo: connettivi logici possono operare solo tra valori booleani
        if type(x) is not bool or type(y) is not bool:
            raise SaltinoRuntimeError(f"Logical operators can only operate on boolean values, got {type(x).__name__} and {type(y).__name__}")
        return operation(x, y)


def exec_saltino_iterative(filename: str) -> Any:
    """Esegue un file Saltino usando l'interprete iterativo."""
    try:
        with open(filename, 'r') as file:
            program_text = file.read()

        # Parse del programma
        input_stream = InputStream(program_text)
        lexer = SaltinoLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = SaltinoParser(token_stream)
        tree = parser.programma()

        # Costruzione dell'AST
        ast = build_ast(tree)

        # Esecuzione con l'interprete iterativo
        interpreter = IterativeSaltinoInterpreter()
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
    if len(sys.argv) != 2:
        print("Usage: python iterative_interpreter.py <saltino_file>")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        result = exec_saltino_iterative(filename)
        print(f"Program result: {result}")
    except SaltinoRuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        sys.exit(0)
