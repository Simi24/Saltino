from antlr4 import InputStream, CommonTokenStream
from AST.ASTsymbol_table import SymbolTable, SymbolKind
from AST.ASTNodes import *
from AST.ASTVisitor import build_ast, print_ast
from AST.semantic_analyzer import SemanticAnalyzer
from Grammatica.SaltinoLexer import SaltinoLexer
from Grammatica.SaltinoParser import SaltinoParser
import sys
import os
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

# Add the workspace root to the Python path
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, workspace_root)


def exec_saltino_with_semantic_analysis(filename: str) -> Any:
    """Esegue un file Saltino con analisi semantica"""
    with open(filename, 'r') as file:
        program_text = file.read()

    # 1. PARSING (il tuo codice esistente)
    print("=== FASE 1: PARSING ===")
    input_stream = InputStream(program_text)
    lexer = SaltinoLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = SaltinoParser(token_stream)
    tree = parser.programma()

    # 2. COSTRUZIONE AST (il tuo codice esistente)
    print("\n=== FASE 2: COSTRUZIONE AST ===")
    ast = build_ast(tree)  # La tua funzione

    # 3. ANALISI SEMANTICA (NUOVO!)
    print("\n=== FASE 3: ANALISI SEMANTICA ===")
    analyzer = SemanticAnalyzer()

    if not analyzer.analyze(ast):
        return None  # Errore nell'analisi semantica

    # Debug: stampa le symbol table
    analyzer.print_symbol_tables()
    
    # Debug: stampa l'AST decorato
    analyzer.print_decorated_ast()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python iterative_interpreter.py <saltino_file>")
        sys.exit(1)

    filename = sys.argv[1]
    result = exec_saltino_with_semantic_analysis(filename)
    print(f"Program result: {result}")

