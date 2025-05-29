#!/usr/bin/env python3
"""
Interprete per il linguaggio Saltino.

Questo interprete utilizza una dispatch table per eseguire il codice
rappresentato dall'AST e fornisce una funzione exec per eseguire
programmi Saltino (.salt).
"""

from Grammatica.SaltinoParser import SaltinoParser
from Grammatica.SaltinoLexer import SaltinoLexer
from AST.ASTVisitor import build_ast
from AST.ASTNodes import *
from antlr4 import InputStream, CommonTokenStream
from typing import Any, Dict, List, Optional, Union
import sys
import os
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


class ReturnValue(Exception):
    """Eccezione usata per implementare il return nelle funzioni."""

    def __init__(self, value: Any):
        self.value = value


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


class SaltinoInterpreter(ASTVisitor):
    """
    Interprete per il linguaggio Saltino.

    Utilizza il pattern Visitor per attraversare l'AST e una dispatch table
    per eseguire le operazioni corrispondenti a ciascun nodo.
    """

    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env

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
        return Environment(parent or self.current_env)

    def _with_environment(self, env: Environment):
        """Context manager per cambiare temporaneamente l'ambiente."""
        class EnvContext:
            def __init__(self, interpreter, new_env):
                self.interpreter = interpreter
                self.new_env = new_env
                self.old_env = None

            def __enter__(self):
                self.old_env = self.interpreter.current_env
                self.interpreter.current_env = self.new_env
                return self.new_env

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.interpreter.current_env = self.old_env

        return EnvContext(self, env)

    def _get_main_arguments(self, main_function: Function) -> List[Any]:
        """
        Ottiene gli argomenti per la funzione main dal'utente.
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

    def _arithmetic_op(self, x: Any, y: Any, operation) -> int:
        """Esegue un'operazione aritmetica con controllo di tipo."""
        # Controllo di tipo: operatori aritmetici possono operare solo tra interi
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

    # ==================== VISITOR METHODS ====================

    def visit_program(self, node: Program) -> Any:
        """Esegue un programma."""
        # Prima registra tutte le funzioni
        for function in node.functions:
            self.global_env.define_function(function.name, function)

        # Cerca la funzione main e la esegue
        try:
            main_function = self.global_env.get_function('main')
            # Se main ha parametri, chiede all'utente di inserirli
            args = self._get_main_arguments(main_function)
            return self._call_function(main_function, args)
        except SaltinoRuntimeError:
            raise SaltinoRuntimeError("No main function found")

    def visit_function(self, node: Function) -> Any:
        """Le funzioni sono già state registrate nel visit_program."""
        return None

    def visit_block(self, node: Block) -> Any:
        """Esegue un blocco di istruzioni."""
        result = None
        for statement in node.statements:
            result = statement.accept(self)
        return result

    def visit_assignment(self, node: Assignment) -> Any:
        """Esegue un assegnamento."""
        value = node.value.accept(self)
        self.current_env.set_variable(node.variable, value)
        return value

    def visit_if_statement(self, node: IfStatement) -> Any:
        """Esegue un'istruzione if-then-else."""
        condition_value = node.condition.accept(self)

        if condition_value:
            return node.then_block.accept(self)
        elif node.else_block:
            return node.else_block.accept(self)
        return None

    def visit_return_statement(self, node: ReturnStatement) -> Any:
        """Esegue un'istruzione return."""
        value = node.value.accept(self) if node.value else None
        raise ReturnValue(value)

    def visit_binary_expression(self, node: BinaryExpression) -> Any:
        """Esegue un'espressione binaria."""
        if node.operator not in self.binary_operators:
            raise SaltinoRuntimeError(
                f"Unknown binary operator: {node.operator}")

        left_value = node.left.accept(self)
        right_value = node.right.accept(self)

        try:
            return self.binary_operators[node.operator](left_value, right_value)
        except Exception as e:
            raise SaltinoRuntimeError(
                f"Error in binary operation {node.operator}: {str(e)}")

    def visit_unary_expression(self, node: UnaryExpression) -> Any:
        """Esegue un'espressione unaria."""
        if node.operator not in self.unary_operators:
            raise SaltinoRuntimeError(
                f"Unknown unary operator: {node.operator}")

        operand_value = node.operand.accept(self)

        try:
            return self.unary_operators[node.operator](operand_value)
        except Exception as e:
            raise SaltinoRuntimeError(
                f"Error in unary operation {node.operator}: {str(e)}")

    def visit_function_call(self, node: FunctionCall) -> Any:
        """Esegue una chiamata di funzione."""
        # La funzione può essere un identificatore o un'espressione più complessa
        if isinstance(node.function, Identifier):
            function_name = node.function.name
            try:
                function = self.current_env.get_function(function_name)
            except SaltinoRuntimeError:
                raise SaltinoRuntimeError(
                    f"Function '{function_name}' not found")
        else:
            raise SaltinoRuntimeError(
                "Complex function expressions not yet supported")

        # Valuta gli argomenti
        argument_values = []
        for arg in node.arguments:
            argument_values.append(arg.accept(self))

        return self._call_function(function, argument_values)

    def _call_function(self, function: Function, arguments: List[Any]) -> Any:
        """Chiama una funzione con gli argomenti specificati."""
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

        # Esegue il corpo della funzione nel nuovo ambiente
        try:
            with self._with_environment(function_env):
                result = function.body.accept(self)
                return result
        except ReturnValue as ret:
            return ret.value

    def visit_integer_literal(self, node: IntegerLiteral) -> int:
        """Restituisce il valore di un letterale intero."""
        return node.value

    def visit_identifier(self, node: Identifier) -> Any:
        """Restituisce il valore di un identificatore."""
        try:
            return self.current_env.get_variable(node.name)
        except SaltinoRuntimeError:
            raise SaltinoRuntimeError(f"Undefined variable: {node.name}")

    def visit_empty_list(self, node: EmptyList) -> List[Any]:
        """Restituisce una lista vuota."""
        return []

    def visit_binary_condition(self, node: BinaryCondition) -> bool:
        """Esegue una condizione binaria."""
        if node.operator not in self.logical_operators:
            raise SaltinoRuntimeError(
                f"Unknown logical operator: {node.operator}")

        left_value = node.left.accept(self)
        
        # Controllo di tipo per il primo operando
        if type(left_value) is not bool:
            raise SaltinoRuntimeError(f"Logical operators can only operate on boolean values, got {type(left_value).__name__}")

        # Short-circuit evaluation per and e or
        if node.operator == 'and' and not left_value:
            return False
        elif node.operator == 'or' and left_value:
            return True

        right_value = node.right.accept(self)
        return self.logical_operators[node.operator](left_value, right_value)

    def visit_unary_condition(self, node: UnaryCondition) -> bool:
        """Esegue una condizione unaria (negazione)."""
        if node.operator != '!':
            raise SaltinoRuntimeError(
                f"Unknown unary condition operator: {node.operator}")

        operand_value = node.operand.accept(self)
        
        # Controllo di tipo: negazione può operare solo su valori booleani
        if type(operand_value) is not bool:
            raise SaltinoRuntimeError(f"Logical negation can only operate on boolean values, got {type(operand_value).__name__}")
            
        return not operand_value

    def visit_comparison_condition(self, node: ComparisonCondition) -> bool:
        """Esegue una condizione di confronto."""
        if node.operator not in self.comparison_operators:
            raise SaltinoRuntimeError(
                f"Unknown comparison operator: {node.operator}")

        left_value = node.left.accept(self)
        right_value = node.right.accept(self)

        try:
            return self.comparison_operators[node.operator](left_value, right_value)
        except Exception as e:
            raise SaltinoRuntimeError(
                f"Error in comparison {node.operator}: {str(e)}")

    def visit_boolean_literal(self, node: BooleanLiteral) -> bool:
        """Restituisce il valore di un letterale booleano."""
        return node.value


# ==================== FUNZIONI PUBBLICHE ====================

def parse_saltino(source_code: str) -> Program:
    """
    Parsifica il codice sorgente Saltino e restituisce l'AST.

    Args:
        source_code: Il codice sorgente da parsificare

    Returns:
        Program: L'AST del programma

    Raises:
        Exception: Se ci sono errori di parsing
    """
    # Crea l'input stream
    input_stream = InputStream(source_code)

    # Crea il lexer
    lexer = SaltinoLexer(input_stream)

    # Crea il token stream
    token_stream = CommonTokenStream(lexer)

    # Crea il parser
    parser = SaltinoParser(token_stream)

    # Parsifica il programma
    parse_tree = parser.programma()

    # Costruisce l'AST
    ast = build_ast(parse_tree)

    return ast


def exec_saltino(source_code: str) -> Any:
    """
    Esegue un programma Saltino.

    Args:
        source_code: Il codice sorgente del programma

    Returns:
        Any: Il risultato dell'esecuzione del programma (return value della funzione main)

    Raises:
        SaltinoRuntimeError: Se ci sono errori durante l'esecuzione
        Exception: Se ci sono errori di parsing
    """
    # Parsifica il codice
    ast = parse_saltino(source_code)

    # Crea l'interprete
    interpreter = SaltinoInterpreter()

    # Esegue il programma
    result = ast.accept(interpreter)

    return result


def exec_saltino_file(file_path: str) -> Any:
    """
    Esegue un file Saltino (.salt).

    Args:
        file_path: Il percorso del file da eseguire

    Returns:
        Any: Il risultato dell'esecuzione del programma

    Raises:
        FileNotFoundError: Se il file non esiste
        SaltinoRuntimeError: Se ci sono errori durante l'esecuzione
        Exception: Se ci sono errori di parsing
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        return exec_saltino(source_code)

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")


# ==================== MAIN ====================

def main():
    """Funzione principale per eseguire l'interprete da linea di comando."""
    if len(sys.argv) != 2:
        print("Usage: python interpreter.py <file.salt>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        result = exec_saltino_file(file_path)
        print(f"Program result: {result}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    except SaltinoRuntimeError as e:
        print(f"Runtime Error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
