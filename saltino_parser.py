#!/usr/bin/env python3
"""
Parser per il linguaggio Saltino.

Questo modulo contiene le funzioni per il parsing del codice sorgente Saltino
utilizzando ANTLR4 e la gestione degli errori personalizzata.
"""

from Grammatica.SaltinoParser import SaltinoParser
from Grammatica.SaltinoLexer import SaltinoLexer
from AST.ASTVisitor import build_ast
from AST.ASTNodes import Program
from antlr4 import InputStream, CommonTokenStream
from errors.custom_error_listener import create_error_listener
from errors.parser_errors import ErrorCollector, SaltinoParseError
from typing import Optional, Tuple


def parse_saltino(input_text: str, raise_on_error: bool = True) -> Tuple[Optional[Program], ErrorCollector]:
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
                raise SaltinoParseError("Parsing failed with errors")
            else:
                return None, error_collector, None

        # Costruisci l'AST se non ci sono errori
        ast = build_ast(tree)

        # Esegui l'analisi semantica
        from AST.semantic_analyzer import SemanticAnalyzer
        semantic_analyzer = SemanticAnalyzer(debug_mode=False)
        semantic_analyzer.error_collector = error_collector  # Passa l'error collector

        try:
            semantic_analyzer.analyze(ast)
        except Exception as semantic_error:
            # Gli errori semantici sono già stati aggiunti all'error_collector
            # dall'analizzatore semantico modificato
            pass

        # Controlla se ci sono errori (inclusi quelli semantici)
        if error_collector.has_errors():
            if raise_on_error:
                raise SaltinoParseError("Analysis failed with errors")
            else:
                return None, error_collector, None

        # Se ci sono stati warning ma non errori, li includiamo nel report
        if error_collector.has_warnings():
            print("Warning durante il parsing:")
            for warning in error_collector.get_warnings():
                print(f"  - {warning}")

        return ast, error_collector, semantic_analyzer

    except Exception as e:
        # Se è già un'eccezione Saltino personalizzata, rilanciala
        if hasattr(e, 'position') and hasattr(e, 'message'):
            if raise_on_error:
                raise e
            else:
                return None, error_collector, None
        else:
            # Altrimenti wrappala in un'eccezione generica
            parse_error = SaltinoParseError(
                f"Errore critico durante il parsing: {str(e)}")
            if raise_on_error:
                raise parse_error
            else:
                error_collector.add_error(parse_error)
                return None, error_collector, None


def parse_saltino_interactive(input_text: str) -> Optional[Program]:
    """
    Funzione di parsing interattiva che mostra errori dettagliati.

    Args:
        input_text: Il codice sorgente da parsare

    Returns:
        L'AST del programma o None se ci sono errori
    """
    try:
        ast, error_collector, semantic_analyzer = parse_saltino(
            input_text, raise_on_error=False)

        if error_collector.has_errors():
            print("❌ Errori durante il parsing:")
            for error in error_collector.errors:
                print(f"  - {error}")
            return None

        if error_collector.has_warnings():
            print("⚠️  Warning durante il parsing:")
            for warning in error_collector.get_warnings():
                print(f"  - {warning}")

        print("✅ Parsing completato con successo")
        return ast

    except Exception as e:
        print(f"❌ Errore critico durante il parsing: {e}")
        return None
