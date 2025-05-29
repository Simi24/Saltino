#!/usr/bin/env python3

import sys
sys.path.append('.')

from Grammatica.SaltinoLexer import SaltinoLexer
from Grammatica.SaltinoParser import SaltinoParser
from AST.ASTVisitor import build_ast, print_ast
from antlr4 import InputStream, CommonTokenStream

def debug_ast(filename):
    with open(filename, 'r') as file:
        code = file.read()
    
    input_stream = InputStream(code)
    lexer = SaltinoLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = SaltinoParser(token_stream)
    
    parse_tree = parser.programma()
    ast = build_ast(parse_tree)
    
    print("AST generato:")
    print(print_ast(ast))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_ast.py <filename>")
        sys.exit(1)
    
    debug_ast(sys.argv[1])
