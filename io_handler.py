"""
User I/O handling module for the Saltino interpreter.
Contains functions for direct user interaction (input/output).
"""

import sys
from typing import List, Any
from AST.ASTNodes import Function


def get_main_arguments(main_function: Function) -> List[Any]:
    """
    Ottiene gli argomenti per la funzione main dall'utente.
    Se main non ha parametri, restituisce una lista vuota.
    Se main ha parametri, chiede all'utente di inserirli.
    """
    if not main_function.parameters:
        return []

    print(
        f"The main function requires {len(main_function.parameters)} parameter(s): {', '.join(main_function.parameters)}")
    print("Please enter the values:")

    args = []
    for param in main_function.parameters:
        while True:
            try:
                user_input = input(f"  {param}: ").strip()

                # Prova a parsare come intero
                if user_input.isdigit() or (user_input.startswith('-') and user_input[1:].isdigit()):
                    args.append(int(user_input))
                    break

                # Prova a parsare come booleano
                elif user_input.lower() in ['true', 'false']:
                    args.append(user_input.lower() == 'true')
                    break

                # Prova a parsare come lista vuota
                elif user_input == '[]':
                    args.append([])
                    break

                else:
                    print(
                        f"    Invalid input. Please enter an integer, 'true', 'false', or '[]'")

            except KeyboardInterrupt:
                print("\nExecution cancelled by user.")
                sys.exit(0)
            except EOFError:
                print("\nNo input provided. Exiting.")
                sys.exit(0)

    return args