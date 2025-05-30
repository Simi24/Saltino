#!/usr/bin/env python3
"""
Operatori per l'interprete Saltino.

Questo modulo contiene le implementazioni di tutti gli operatori
supportati dal linguaggio Saltino con controlli di tipo appropriati.
"""

from typing import Any, List, Union
from errors.runtime_errors import SaltinoRuntimeError


class SaltinoOperators:
    """Classe che contiene tutti gli operatori del linguaggio Saltino."""

    @staticmethod
    def safe_divide(x: Union[int, float], y: Union[int, float]) -> Union[int, float]:
        """Divisione sicura che controlla la divisione per zero."""
        # Controllo di tipo: operatori aritmetici possono operare solo tra interi
        if type(x) is not int or type(y) is not int:
            raise SaltinoRuntimeError(
                f"Arithmetic operators can only operate on integers, got {type(x).__name__} and {type(y).__name__}")
        if y == 0:
            raise SaltinoRuntimeError("Division by zero")
        return x // y  # Divisione intera per mantenere il tipo intero

    @staticmethod
    def cons(head: Any, tail: List[Any]) -> List[Any]:
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
                    f"Cons operator expects a list of integers, got {type(item).__name__} at position {i}")
        return [head] + tail

    @staticmethod
    def head(lst: List[Any]) -> Any:
        """Restituisce il primo elemento di una lista."""
        if not isinstance(lst, list):
            raise SaltinoRuntimeError(
                f"Head operator expects a list, got {type(lst)}")
        if len(lst) == 0:
            raise SaltinoRuntimeError("Head of empty list")
        return lst[0]

    @staticmethod
    def tail(lst: List[Any]) -> List[Any]:
        """Restituisce la coda di una lista (tutti gli elementi tranne il primo)."""
        if not isinstance(lst, list):
            raise SaltinoRuntimeError(
                f"Tail operator expects a list, got {type(lst)}")
        if len(lst) == 0:
            raise SaltinoRuntimeError("Tail of empty list")
        return lst[1:]

    @staticmethod
    def arithmetic_op(x: Any, y: Any, operation) -> int:
        """Esegue un'operazione aritmetica con controllo di tipo."""
        # Controllo di tipo: operatori aritmetici possono operare solo tra interi
        # Nota: isinstance(True, int) è True in Python, quindi controlliamo esplicitamente bool
        if type(x) is not int or type(y) is not int:
            raise SaltinoRuntimeError(
                f"Arithmetic operators can only operate on integers, got {type(x).__name__} and {type(y).__name__}")
        return operation(x, y)

    @staticmethod
    def unary_arithmetic_op(x: Any, operation) -> int:
        """Esegue un'operazione aritmetica unaria con controllo di tipo."""
        # Controllo di tipo: operatori aritmetici possono operare solo su interi
        if type(x) is not int:
            raise SaltinoRuntimeError(
                f"Unary arithmetic operators can only operate on integers, got {type(x).__name__}")
        return operation(x)

    @staticmethod
    def comparison_op(x: Any, y: Any, operation) -> bool:
        """Esegue un'operazione di confronto con controllo di tipo."""
        # Controllo di tipo: operatori di confronto (eccetto ==) possono operare solo su interi
        if type(x) is not int or type(y) is not int:
            raise SaltinoRuntimeError(
                f"Comparison operators can only operate on integers, got {type(x).__name__} and {type(y).__name__}")
        return operation(x, y)

    @staticmethod
    def equality_comparison(x: Any, y: Any) -> bool:
        """Esegue il confronto di uguaglianza con regole speciali."""
        # == può operare su interi o tra liste di interi, dove una deve essere []
        if type(x) is int and type(y) is int:
            return x == y
        elif isinstance(x, list) and isinstance(y, list):
            return x == y
        else:
            return False

    @staticmethod
    def logical_op(x: Any, y: Any, operation) -> bool:
        """Esegue un'operazione logica con controllo di tipo."""
        # Controllo di tipo: connettivi logici possono operare solo tra valori booleani
        if type(x) is not bool or type(y) is not bool:
            raise SaltinoRuntimeError(
                f"Logical operators can only operate on booleans, got {type(x).__name__} and {type(y).__name__}")
        return operation(x, y)

    @classmethod
    def get_binary_operators(cls):
        """Restituisce la dispatch table per le operazioni binarie."""
        return {
            '+': lambda x, y: cls.arithmetic_op(x, y, lambda a, b: a + b),
            '-': lambda x, y: cls.arithmetic_op(x, y, lambda a, b: a - b),
            '*': lambda x, y: cls.arithmetic_op(x, y, lambda a, b: a * b),
            '/': lambda x, y: cls.safe_divide(x, y),
            '%': lambda x, y: cls.arithmetic_op(x, y, lambda a, b: a % b),
            '^': lambda x, y: cls.arithmetic_op(x, y, lambda a, b: a ** b),
            '::': lambda x, y: cls.cons(x, y),
        }

    @classmethod
    def get_unary_operators(cls):
        """Restituisce la dispatch table per le operazioni unarie."""
        return {
            '+': lambda x: cls.unary_arithmetic_op(x, lambda a: +a),
            '-': lambda x: cls.unary_arithmetic_op(x, lambda a: -a),
            'head': lambda x: cls.head(x),
            'tail': lambda x: cls.tail(x),
        }

    @classmethod
    def get_comparison_operators(cls):
        """Restituisce la dispatch table per gli operatori di confronto."""
        return {
            '==': lambda x, y: cls.equality_comparison(x, y),
            '!=': lambda x, y: cls.comparison_op(x, y, lambda a, b: a != b),
            '<': lambda x, y: cls.comparison_op(x, y, lambda a, b: a < b),
            '<=': lambda x, y: cls.comparison_op(x, y, lambda a, b: a <= b),
            '>': lambda x, y: cls.comparison_op(x, y, lambda a, b: a > b),
            '>=': lambda x, y: cls.comparison_op(x, y, lambda a, b: a >= b),
        }

    @classmethod
    def get_logical_operators(cls):
        """Restituisce la dispatch table per le operazioni logiche."""
        return {
            'and': lambda x, y: cls.logical_op(x, y, lambda a, b: a and b),
            'or': lambda x, y: cls.logical_op(x, y, lambda a, b: a or b),
        }
