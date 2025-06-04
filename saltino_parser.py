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
from errors.parser_errors import SaltinoParseError
from typing import Optional, Tuple, List, Dict, Any


def parse_saltino(input_text: str, raise_on_error: bool = True, debug_mode = False) -> Tuple[Optional[Program], List[Dict[str, Any]], Optional[Any]]:
    """
    Analizza il codice sorgente Saltino e genera l'AST.

    Args:
        input_text: Il codice sorgente da analizzare
        raise_on_error: Se True, lancia eccezioni per errori di parsing

    Returns:
        tuple: (ast, errors, semantic_analyzer) dove:
               - ast: L'AST del programma (None se ci sono errori)
               - errors: Lista degli errori di parsing
               - semantic_analyzer: L'analizzatore semantico utilizzato

    Raises:
        SaltinoParseError: Se ci sono errori di parsing e raise_on_error è True
    """
    try:
        # Crea lo stream di input
        input_stream = InputStream(input_text)

        # Crea il lexer con custom error listener
        lexer = SaltinoLexer(input_stream)
        lexer_error_listener = create_error_listener()
        lexer.removeErrorListeners()  # Rimuovi i listener di default
        lexer.addErrorListener(lexer_error_listener)

        # Crea lo stream di token
        token_stream = CommonTokenStream(lexer)

        # Crea il parser con custom error listener
        parser = SaltinoParser(token_stream)
        parser_error_listener = create_error_listener()
        parser.removeErrorListeners()  # Rimuovi i listener di default
        parser.addErrorListener(parser_error_listener)

        # Parsa il programma
        tree = parser.programma()

        # Combina gli errori del lexer e del parser
        all_errors = lexer_error_listener.get_errors() + parser_error_listener.get_errors()

        # Controlla se ci sono stati errori di parsing
        if all_errors:
            if raise_on_error:
                error_msg = "\n".join([f"Riga {err['line']}, colonna {err['column']}: {err['message']}"
                                       for err in all_errors])
                raise SaltinoParseError(
                    f"Parsing failed with errors:\n{error_msg}")
            else:
                return None, all_errors, None

        # Costruisci l'AST se non ci sono errori
        ast = build_ast(tree)

        # Esegui l'analisi semantica
        from AST.semantic_analyzer import SemanticAnalyzer
        from tail_recursive_transformer import TailCallTransformer
        semantic_analyzer = SemanticAnalyzer(debug_mode=debug_mode)
        tail_recursive_transformer = TailCallTransformer()

        try:
            ast = tail_recursive_transformer.transform_program(ast)
            semantic_analyzer.analyze(ast)
            # Se l'analisi semantica ha successo, non ci sono errori aggiuntivi
            return ast, all_errors, semantic_analyzer
        except Exception as semantic_error:
            # Aggiungi l'errore semantico agli errori esistenti
            semantic_err = {
                'line': getattr(semantic_error, 'line', 0),
                'column': getattr(semantic_error, 'column', 0),
                'message': str(semantic_error),
                'type': 'semantic'
            }
            all_errors.append(semantic_err)

            if raise_on_error:
                raise semantic_error
            else:
                return None, all_errors, semantic_analyzer

    except Exception as e:
        # Se è già un'eccezione Saltino personalizzata, rilanciala
        if isinstance(e, SaltinoParseError):
            if raise_on_error:
                raise
            else:
                # Crea un errore generico
                generic_error = {
                    'line': 0,
                    'column': 0,
                    'message': str(e),
                    'type': 'parsing'
                }
                return None, [generic_error], None

        # Per altre eccezioni, crea un errore generico
        if raise_on_error:
            raise SaltinoParseError(
                f"Unexpected error during parsing: {str(e)}")
        else:
            generic_error = {
                'line': 0,
                'column': 0,
                'message': f"Errore inaspettato durante il parsing: {str(e)}",
                'type': 'unexpected'
            }
            return None, [generic_error], None


def parse_saltino_interactive(input_text: str) -> Optional[Program]:
    """
    Funzione di parsing interattiva che mostra errori dettagliati.

    Args:
        input_text: Il codice sorgente da parsare

    Returns:
        L'AST del programma o None se ci sono errori
    """
    try:
        ast, errors, semantic_analyzer = parse_saltino(
            input_text, raise_on_error=False)

        if errors:
            print("❌ Errori durante il parsing:")
            for error in errors:
                error_type = error.get('type', 'unknown')
                print(
                    f"  - Riga {error['line']}, colonna {error['column']} ({error_type}): {error['message']}")
            return None

        print("✅ Parsing completato con successo!")
        return ast

    except Exception as e:
        print(f"❌ Errore critico durante il parsing: {e}")
        return None
