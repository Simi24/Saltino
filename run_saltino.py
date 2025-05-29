#!/usr/bin/env python3
"""
Launcher per eseguire programmi Saltino con l'interprete ottimizzato.

Utilizzo:
    python run_saltino.py <programma>                 # Esegue un programma con ottimizzazioni
    python run_saltino.py <programma> --no-opt        # Esegue senza ottimizzazioni
    python run_saltino.py --list                      # Lista programmi disponibili
    python run_saltino.py --all                       # Esegue tutti i programmi
    python run_saltino.py --demo                      # Esegue le demo

Esempi:
    python run_saltino.py factorial
    python run_saltino.py programs/factorial.salt
    python run_saltino.py fibonacci --no-opt
"""

import sys
import os
import argparse

# Aggiungi il percorso corrente al path per importare i moduli
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from optimized_interpreter import (
    run_program_from_directory, 
    list_programs, 
    run_all_programs,
    exec_saltino_file
)


def main():
    parser = argparse.ArgumentParser(
        description="Esegue programmi Saltino con l'interprete ottimizzato",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('program', nargs='?', help='Nome del programma da eseguire')
    parser.add_argument('--no-opt', action='store_true', 
                       help='Disabilita le ottimizzazioni tail-recursive')
    parser.add_argument('--list', action='store_true',
                       help='Lista tutti i programmi disponibili')
    parser.add_argument('--all', action='store_true',
                       help='Esegue tutti i programmi disponibili')
    parser.add_argument('--demo', action='store_true',
                       help='Esegue le demo dell\'interprete ottimizzato')
    parser.add_argument('--dir', default='programs',
                       help='Directory contenente i programmi (default: programs)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Output verboso')
    
    args = parser.parse_args()
    
    # Determina se abilitare le ottimizzazioni
    enable_optimizations = not args.no_opt
    
    try:
        # Lista programmi
        if args.list:
            programs = list_programs(args.dir)
            print(f"Programmi disponibili in {args.dir}/:")
            for program in programs:
                print(f"  - {program}")
            return 0
        
        # Esegui tutti i programmi
        elif args.all:
            opt_status = "con" if enable_optimizations else "senza"
            print(f"Eseguendo tutti i programmi {opt_status} ottimizzazioni...")
            results = run_all_programs(args.dir, enable_optimizations)
            
            # Conta successi e fallimenti
            successes = sum(1 for r in results.values() if not str(r).startswith("ERRORE"))
            failures = len(results) - successes
            
            print(f"\nRisultato finale: {successes} successi, {failures} fallimenti")
            return 0 if failures == 0 else 1
        
        # Demo
        elif args.demo:
            print("Eseguendo demo dell'interprete ottimizzato...")
            from optimized_interpreter import demo_optimized_interpreter, demo_programs_directory
            demo_optimized_interpreter()
            demo_programs_directory()
            return 0
        
        # Esegui un programma specifico
        elif args.program:
            # Determina se è un percorso completo o solo un nome
            if os.path.sep in args.program or args.program.endswith('.salt'):
                # Percorso completo o con estensione
                if not os.path.exists(args.program):
                    print(f"Errore: File {args.program} non trovato")
                    return 1
                
                result = exec_saltino_file(args.program, enable_optimizations)
                
                if args.verbose:
                    opt_status = "con" if enable_optimizations else "senza"
                    print(f"Eseguito {args.program} {opt_status} ottimizzazioni")
                    print(f"Risultato: {result}")
                else:
                    print(result)
            else:
                # Solo nome del programma - cerca nella directory
                result = run_program_from_directory(
                    args.program, 
                    args.dir, 
                    enable_optimizations, 
                    verbose=args.verbose
                )
                
                if not args.verbose:
                    print(result)
            
            return 0
        
        else:
            # Nessun argomento - mostra help
            parser.print_help()
            return 0
            
    except FileNotFoundError as e:
        print(f"Errore: {e}")
        return 1
    except Exception as e:
        print(f"Errore durante l'esecuzione: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
