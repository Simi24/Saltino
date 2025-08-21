#!/usr/bin/env python3
"""
Main entry point for the Saltino interpreter.
Handles command-line argument parsing and program execution.
"""

import sys
from typing import Any
from interpreter import IterativeSaltinoInterpreter
from saltino_parser import parse_saltino
from errors.parser_errors import SaltinoParseError, SaltinoError
from errors.runtime_errors import SaltinoRuntimeError


def exec_saltino_iterative(filename: str, debug_mode: bool = False) -> Any:
    """Esegue un file Saltino usando l'interprete iterativo con gestione errori personalizzata."""
    try:
        with open(filename, 'r') as file:
            program_text = file.read()

        ast, errors, semantic_analyzer = parse_saltino(
            program_text, raise_on_error=False, debug_mode=debug_mode)

        # Controlla se ci sono stati errori di parsing
        if errors:
            print("❌ Errori durante il parsing:")
            for error in errors:
                error_type = error.get('type', 'unknown')
                print(
                    f"  - Riga {error['line']}, colonna {error['column']} ({error_type}): {error['message']}")
            raise SaltinoRuntimeError(
                "Errori di parsing impediscono l'esecuzione")

        if ast is None:
            raise SaltinoRuntimeError("Errore nella costruzione dell'AST")

        # Esecuzione con l'interprete iterativo
        interpreter = IterativeSaltinoInterpreter(debug_mode=debug_mode)
        interpreter.semantic_analyzer = semantic_analyzer  # Passa il semantic analyzer
        result = interpreter.execute_program(ast)

        # Stampa le statistiche di esecuzione
        interpreter.print_execution_stats()

        return result

    except FileNotFoundError:
        raise SaltinoRuntimeError(f"File not found: {filename}")
    except (SaltinoParseError, SaltinoError) as e:
        # Gli errori di parsing e semantici non sono errori di runtime
        raise e
    except Exception as e:
        if isinstance(e, SaltinoRuntimeError):
            raise e
        else:
            raise SaltinoRuntimeError(f"Error executing {filename}: {str(e)}")


if __name__ == "__main__":
    debug_mode = False
    filename = None

    # Parse degli argomenti
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--debug":
            debug_mode = True
        elif not arg.startswith("--"):
            filename = arg

    if filename is None:
        print("Usage: python main.py <saltino_file> [--debug]")
        print("\nOptions:")
        print("  --debug    Enable debug mode with verbose output")
        sys.exit(1)

    try:
        result = exec_saltino_iterative(filename, debug_mode=debug_mode)
        print(f"Program result: {result}")
    except (SaltinoParseError, SaltinoError) as e:
        print(f"Parse/Semantic Error: {e}")
        sys.exit(1)
    except SaltinoRuntimeError as e:
        print(f"{e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        sys.exit(0)
