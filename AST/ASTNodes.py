"""
Definizione dei nodi AST per il linguaggio Saltino.

Gerarchia delle classi:
- ASTNode (classe base)
  - Program
  - Function
  - Statement
    - Assignment
    - IfStatement
    - ReturnStatement
    - Block
  - Expression
    - BinaryExpression
    - UnaryExpression
    - FunctionCall
    - IntegerLiteral
    - BooleanLiteral
    - Identifier
    - EmptyList
  - Condition
    - BinaryCondition
    - UnaryCondition
    - ComparisonCondition
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union, Any


class SourcePosition:
    """Informazioni sulla posizione nel codice sorgente per error reporting."""

    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column

    def __str__(self):
        return f"line {self.line}, col {self.column}"


class ASTNode(ABC):
    """Classe base per tutti i nodi AST."""

    def __init__(self, position: Optional[SourcePosition] = None):
        self.position = position

    @abstractmethod
    def accept(self, visitor):
        """Pattern Visitor per attraversare l'AST."""
        pass

    def __str__(self):
        return self.__class__.__name__


# ==================== NODI DI LIVELLO SUPERIORE ====================

class Program(ASTNode):
    """Nodo radice che rappresenta un programma completo."""

    def __init__(self, functions: List['Function'], position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.functions = functions

    def accept(self, visitor):
        return visitor.visit_program(self)

    def __str__(self):
        return f"Program({len(self.functions)} functions)"


class Function(ASTNode):
    """Definizione di una funzione."""

    def __init__(self, name: str, parameters: List[str], body: 'Block',
                 position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.name = name
        self.parameters = parameters
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function(self)

    def __str__(self):
        params = ', '.join(self.parameters)
        return f"Function({self.name}({params}))"


# ==================== STATEMENTS ====================

class Statement(ASTNode):
    """Classe base per tutte le istruzioni."""
    pass


class Block(Statement):
    """Blocco di istruzioni racchiuso tra graffe."""

    def __init__(self, statements: List[Union[Statement, 'Block']],
                 position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block(self)

    def __str__(self):
        return f"Block({len(self.statements)} statements)"


class Assignment(Statement):
    """Assegnamento di variabile."""

    def __init__(self, variable: str, value: Union['Expression', 'Condition'],
                 position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.variable = variable
        self.value = value

    def accept(self, visitor):
        return visitor.visit_assignment(self)

    def __str__(self):
        return f"Assignment({self.variable} = {self.value})"


class IfStatement(Statement):
    """Istruzione if-then-else."""

    def __init__(self, condition: 'Condition', then_block: Block,
                 else_block: Optional[Block] = None,
                 position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def accept(self, visitor):
        return visitor.visit_if_statement(self)

    def __str__(self):
        else_part = f" else {self.else_block}" if self.else_block else ""
        return f"IfStatement(if {self.condition} then {self.then_block}{else_part})"


class ReturnStatement(Statement):
    """Istruzione return."""

    def __init__(self, value: Union['Expression', 'Condition'],
                 position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.value = value

    def accept(self, visitor):
        return visitor.visit_return_statement(self)

    def __str__(self):
        return f"ReturnStatement(return {self.value})"


# ==================== EXPRESSIONS ====================

class Expression(ASTNode):
    """Classe base per tutte le espressioni."""
    pass


class BinaryExpression(Expression):
    """Espressione binaria (operatore con due operandi)."""

    def __init__(self, left: Expression, operator: str, right: Expression,
                 position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expression(self)

    def __str__(self):
        return f"BinaryExpression({self.left} {self.operator} {self.right})"


class UnaryExpression(Expression):
    """Espressione unaria (operatore con un operando)."""

    def __init__(self, operator: str, operand: Expression,
                 position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.operator = operator
        self.operand = operand

    def accept(self, visitor):
        return visitor.visit_unary_expression(self)

    def __str__(self):
        return f"UnaryExpression({self.operator} {self.operand})"


class FunctionCall(Expression):
    """Chiamata di funzione."""

    def __init__(self, function: Expression, arguments: List[Union[Expression, 'Condition']],
                 position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.function = function
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit_function_call(self)

    def __str__(self):
        args = ', '.join(str(arg) for arg in self.arguments)
        return f"FunctionCall({self.function}({args}))"


class IntegerLiteral(Expression):
    """Letterale intero."""

    def __init__(self, value: int, position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.value = value

    def accept(self, visitor):
        return visitor.visit_integer_literal(self)

    def __str__(self):
        return f"IntegerLiteral({self.value})"


class Identifier(Expression):
    """Identificatore (nome di variabile o funzione)."""

    def __init__(self, name: str, position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.name = name

    def accept(self, visitor):
        return visitor.visit_identifier(self)

    def __str__(self):
        return f"Identifier({self.name})"


class EmptyList(Expression):
    """Lista vuota []."""

    def __init__(self, position: Optional[SourcePosition] = None):
        super().__init__(position)

    def accept(self, visitor):
        return visitor.visit_empty_list(self)

    def __str__(self):
        return "EmptyList([])"


# ==================== CONDITIONS ====================

class Condition(ASTNode):
    """Classe base per tutte le condizioni."""
    pass


class BinaryCondition(Condition):
    """Condizione binaria (and, or)."""

    def __init__(self, left: Condition, operator: str, right: Condition,
                 position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_condition(self)

    def __str__(self):
        return f"BinaryCondition({self.left} {self.operator} {self.right})"


class UnaryCondition(Condition):
    """Condizione unaria (negazione !)."""

    def __init__(self, operator: str, operand: Condition,
                 position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.operator = operator
        self.operand = operand

    def accept(self, visitor):
        return visitor.visit_unary_condition(self)

    def __str__(self):
        return f"UnaryCondition({self.operator} {self.operand})"


class ComparisonCondition(Condition):
    """Condizione di confronto tra espressioni."""

    def __init__(self, left: Expression, operator: str, right: Expression,
                 position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_comparison_condition(self)

    def __str__(self):
        return f"ComparisonCondition({self.left} {self.operator} {self.right})"


class BooleanLiteral(Expression):
    """Letterale booleano (true, false)."""

    def __init__(self, value: bool, position: Optional[SourcePosition] = None):
        super().__init__(position)
        self.value = value

    def accept(self, visitor):
        return visitor.visit_boolean_literal(self)

    def __str__(self):
        return f"BooleanLiteral({self.value})"


# ==================== VISITOR INTERFACE ====================

class ASTVisitor(ABC):
    """Interfaccia per il pattern Visitor sui nodi AST."""

    @abstractmethod
    def visit_program(self, node: Program): pass

    @abstractmethod
    def visit_function(self, node: Function): pass

    @abstractmethod
    def visit_block(self, node: Block): pass

    @abstractmethod
    def visit_assignment(self, node: Assignment): pass

    @abstractmethod
    def visit_if_statement(self, node: IfStatement): pass

    @abstractmethod
    def visit_return_statement(self, node: ReturnStatement): pass

    @abstractmethod
    def visit_binary_expression(self, node: BinaryExpression): pass

    @abstractmethod
    def visit_unary_expression(self, node: UnaryExpression): pass

    @abstractmethod
    def visit_function_call(self, node: FunctionCall): pass

    @abstractmethod
    def visit_integer_literal(self, node: IntegerLiteral): pass

    @abstractmethod
    def visit_identifier(self, node: Identifier): pass

    @abstractmethod
    def visit_empty_list(self, node: EmptyList): pass

    @abstractmethod
    def visit_binary_condition(self, node: BinaryCondition): pass

    @abstractmethod
    def visit_unary_condition(self, node: UnaryCondition): pass

    @abstractmethod
    def visit_comparison_condition(self, node: ComparisonCondition): pass

    @abstractmethod
    def visit_boolean_literal(self, node: BooleanLiteral): pass
