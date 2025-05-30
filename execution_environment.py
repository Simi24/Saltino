#!/usr/bin/env python3
"""
Ambiente di esecuzione per l'interprete Saltino.

Questo modulo contiene la classe Environment che gestisce le variabili
e le funzioni durante l'esecuzione, utilizzando i nomi semantici univoci.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING
from errors.runtime_errors import SaltinoRuntimeError

# Import condizionale per evitare import circolari
if TYPE_CHECKING:
    from AST.ASTNodes import ASTNode, Function, Identifier, Assignment
    from AST.semantic_analyzer import SemanticAnalyzer
else:
    ASTNode = Any
    Function = Any
    Identifier = Any
    Assignment = Any
    SemanticAnalyzer = Any


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
        self.functions: Dict[str, Any] = {}

    def get_unique_name(self, node: Any, semantic_analyzer: Any) -> str:
        """
        Ottiene il nome univoco per un nodo dall'analizzatore semantico.
        Usato per identificatori e assegnamenti.
        """
        # Importiamo i tipi localmente per evitare problemi circolari
        from AST.ASTNodes import Identifier, Assignment
        
        if isinstance(node, Identifier):
            # Per gli identificatori, cerca nella symbol table
            scope = semantic_analyzer.get_node_info(node, 'scope')
            if scope:
                try:
                    symbol_info = scope.lookup(node.name)
                    return symbol_info.unique_name
                except ValueError:
                    raise SaltinoRuntimeError(f"Undefined variable: {node.name}")
            else:
                raise SaltinoRuntimeError(f"No scope information for identifier: {node.name}")
        elif isinstance(node, Assignment):
            # Per gli assegnamenti, cerca le informazioni della variabile
            var_info = semantic_analyzer.get_node_info(node, 'variable_info')
            if var_info:
                return var_info.unique_name
            else:
                raise SaltinoRuntimeError(f"No variable info for assignment: {node.variable_name}")
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

    def define_function(self, name: str, function: Any):
        """Definisce una funzione nell'ambiente corrente."""
        self.functions[name] = function

    def get_function(self, name: str) -> Any:
        """Ottiene una funzione per nome."""
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        else:
            raise SaltinoRuntimeError(f"Undefined function: {name}")
