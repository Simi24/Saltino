"""
Pacchetto AST per il linguaggio Saltino.

Contiene:
- ASTNodes: Definizioni delle classi per i nodi AST
- ASTVisitor: Visitor per costruire l'AST dal parse tree
"""

from .ASTNodes import *
from .ASTVisitor import SaltinoASTVisitor, build_ast, print_ast

__all__ = [
    # Nodi AST
    'ASTNode', 'SourcePosition',
    'Program', 'Function',
    'Statement', 'Block', 'Assignment', 'IfStatement', 'ReturnStatement',
    'Expression', 'BinaryExpression', 'UnaryExpression', 'FunctionCall',
    'IntegerLiteral', 'Identifier', 'EmptyList',
    'Condition', 'BinaryCondition', 'UnaryCondition', 'ComparisonCondition',
    'BooleanLiteral',
    'ASTVisitor',
    
    # Visitor e utility
    'SaltinoASTVisitor', 'build_ast', 'print_ast'
]
