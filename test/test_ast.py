#!/usr/bin/env python3
"""
Script di test per l'AST di Saltino.

Testa la costruzione dell'AST con esempi semplici.
"""

import sys
import os

# Aggiungi il percorso del progetto al PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from antlr4 import InputStream, CommonTokenStream
from Grammatica.SaltinoLexer import SaltinoLexer
from Grammatica.SaltinoParser import SaltinoParser
from AST import build_ast, print_ast
from AST.ASTVisitor import SaltinoASTVisitor


def test_simple_function():
    """Test con una funzione semplice."""
    print("=== Test: Funzione Semplice ===")
    
    code = """
    def main() {
        x = 42
        return x
    }
    """
    
    try:
        # Parsing
        input_stream = InputStream(code)
        lexer = SaltinoLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = SaltinoParser(token_stream)
        
        # Genera il parse tree
        parse_tree = parser.programma()
        
        # Costruisci l'AST
        visitor = SaltinoASTVisitor()
        ast = visitor.visitProgramma(parse_tree)
        
        # Stampa l'AST
        print("AST generato:")
        print(print_ast(ast))
        
        print("✓ Test completato con successo!")
        
    except Exception as e:
        print(f"✗ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()


def test_function_with_parameters():
    """Test con una funzione con parametri."""
    print("\n=== Test: Funzione con Parametri ===")
    
    code = """
    def add(a, b) {
        result = a + b
        return result
    }
    """
    
    try:
        input_stream = InputStream(code)
        lexer = SaltinoLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = SaltinoParser(token_stream)
        
        parse_tree = parser.programma()
        ast = build_ast(parse_tree)
        
        print("AST generato:")
        print(print_ast(ast))
        
        print("✓ Test completato con successo!")
        
    except Exception as e:
        print(f"✗ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()


def test_if_statement():
    """Test con una struttura if-then-else."""
    print("\n=== Test: If-Then-Else ===")
    
    code = """
    def max(a, b) {
        if a > b then {
            return a
        } else {
            return b
        }
    }
    """
    
    try:
        input_stream = InputStream(code)
        lexer = SaltinoLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = SaltinoParser(token_stream)
        
        parse_tree = parser.programma()
        ast = build_ast(parse_tree)
        
        print("AST generato:")
        print(print_ast(ast))
        
        print("✓ Test completato con successo!")
        
    except Exception as e:
        print(f"✗ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()


def test_complex_expression():
    """Test con espressioni complesse."""
    print("\n=== Test: Espressioni Complesse ===")
    
    code = """
    def calc(x, y) {
        result = (x + y) * 2 ^ 3
        list = x :: []
        return head(list)
    }
    """
    
    try:
        input_stream = InputStream(code)
        lexer = SaltinoLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = SaltinoParser(token_stream)
        
        parse_tree = parser.programma()
        ast = build_ast(parse_tree)
        
        print("AST generato:")
        print(print_ast(ast))
        
        print("✓ Test completato con successo!")
        
    except Exception as e:
        print(f"✗ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()


def test_boolean_conditions():
    """Test con condizioni booleane."""
    print("\n=== Test: Condizioni Booleane ===")
    
    code = """
    def check(x, y) {
        if x > 0 and y < 10 then {
            flag = true
        } else {
            flag = false
        }
        return flag
    }
    """
    
    try:
        input_stream = InputStream(code)
        lexer = SaltinoLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = SaltinoParser(token_stream)
        
        parse_tree = parser.programma()
        ast = build_ast(parse_tree)
        
        print("AST generato:")
        print(print_ast(ast))
        
        print("✓ Test completato con successo!")
        
    except Exception as e:
        print(f"✗ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🧪 Test AST per Saltino")
    print("=" * 50)
    
    test_simple_function()
    test_function_with_parameters()
    test_if_statement()
    test_complex_expression()
    test_boolean_conditions()
    
    print("\n" + "=" * 50)
    print("🏁 Test completati!")
