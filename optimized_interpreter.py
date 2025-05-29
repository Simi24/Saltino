"""
Modulo di integrazione per le trasformazioni tail-recursive nell'interprete.

Questo modulo modifica l'interprete esistente per applicare automaticamente
le trasformazioni tail-recursive quando possibile, senza cambiare l'API
dell'interprete stesso.
"""

from transformation_pipeline import build_transformed_ast
from interpreter import SaltinoInterpreter, parse_saltino
import sys
import os
from typing import Any, List, Dict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class OptimizedSaltinoInterpreter:
    """
    Wrapper ottimizzato per l'interprete che applica trasformazioni tail-recursive.

    Questa classe fornisce un'interfaccia simile all'interprete originale
    ma con preprocessing delle trasformazioni.
    """

    def __init__(self, enable_tail_recursive_optimization: bool = True):
        """
        Inizializza l'interprete ottimizzato.

        Args:
            enable_tail_recursive_optimization: Se abilitare le trasformazioni
        """
        self.tail_recursive_optimization = enable_tail_recursive_optimization
        self.transformation_stats = {
            'functions_analyzed': 0,
            'functions_transformed': 0,
            'transformations_applied': []
        }

    def _preprocess_code(self, code: str):
        """
        Preprocessa il codice applicando le trasformazioni tail-recursive.

        Args:
            code: Il codice sorgente

        Returns:
            Il codice (eventualmente trasformato) e le statistiche
        """
        if not self.tail_recursive_optimization:
            # Resetta le statistiche
            self.transformation_stats = {
                'functions_analyzed': 0,
                'functions_transformed': 0,
                'transformations_applied': []
            }
            return code

        # Applica le trasformazioni
        ast = build_transformed_ast(code, apply_tail_recursive=True)

        # Aggiorna le statistiche
        original_ast = build_transformed_ast(code, apply_tail_recursive=False)

        self.transformation_stats['functions_analyzed'] = len(
            original_ast.functions)
        self.transformation_stats['functions_transformed'] = len(ast.functions)

        if len(ast.functions) > len(original_ast.functions):
            # Identifica quali funzioni sono state trasformate
            original_names = {f.name for f in original_ast.functions}
            new_names = {f.name for f in ast.functions}
            aux_functions = new_names - original_names

            self.transformation_stats['transformations_applied'] = []
            for aux_name in aux_functions:
                base_name = aux_name.replace('_aux', '')
                if base_name in original_names:
                    self.transformation_stats['transformations_applied'].append({
                        'original': base_name,
                        'auxiliary': aux_name
                    })

        # Per ora, dato che non abbiamo un code generator dall'AST,
        # usiamo l'interprete direttamente sull'AST trasformato
        return ast

    def exec_string(self, code: str) -> any:
        """
        Esegue codice Saltino da stringa con ottimizzazioni tail-recursive.

        Args:
            code: Il codice sorgente da eseguire

        Returns:
            Il risultato dell'esecuzione
        """
        if self.tail_recursive_optimization:
            # Applica preprocessing e ottimizzazioni
            optimized_ast = self._preprocess_code(code)

            # Esegue direttamente l'AST trasformato
            interpreter = SaltinoInterpreter()
            return optimized_ast.accept(interpreter)
        else:
            # Usa l'interprete standard
            from interpreter import exec_saltino
            self._preprocess_code(code)  # Solo per aggiornare le statistiche
            return exec_saltino(code)

    def exec_file(self, filepath: str) -> any:
        """
        Esegue un file Saltino con ottimizzazioni tail-recursive.

        Args:
            filepath: Percorso del file da eseguire

        Returns:
            Il risultato dell'esecuzione
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()

        return self.exec_string(code)

    def get_optimization_stats(self) -> dict:
        """
        Ritorna le statistiche delle ottimizzazioni applicate.

        Returns:
            Dizionario con le statistiche
        """
        return {
            'tail_recursive_optimization_enabled': self.tail_recursive_optimization,
            **self.transformation_stats
        }

    def print_optimization_report(self):
        """Stampa un report delle ottimizzazioni applicate."""
        stats = self.get_optimization_stats()

        print("=== REPORT OTTIMIZZAZIONI ===")
        print(
            f"Ottimizzazione tail-recursive: {'Abilitata' if stats['tail_recursive_optimization_enabled'] else 'Disabilitata'}")

        if stats['tail_recursive_optimization_enabled']:
            print(f"Funzioni analizzate: {stats['functions_analyzed']}")
            print(
                f"Funzioni nel programma finale: {stats['functions_transformed']}")

            if stats['transformations_applied']:
                print("Trasformazioni applicate:")
                for transform in stats['transformations_applied']:
                    print(
                        f"  - {transform['original']} → {transform['original']} + {transform['auxiliary']}")
            else:
                print("Nessuna trasformazione applicata")
        print("==============================")


# ==================== COMPATIBILITY FUNCTIONS ====================

def exec_saltino(source_code: str, use_optimizations: bool = True, show_stats: bool = False) -> Any:
    """
    Esegue un programma Saltino con ottimizzazioni opzionali.

    Funzione compatibile con l'interprete originale.

    Args:
        source_code: Il codice sorgente del programma
        use_optimizations: Se True applica le trasformazioni AST (default: True)
        show_stats: Se True mostra statistiche sulle trasformazioni (default: False)

    Returns:
        Any: Il risultato dell'esecuzione del programma

    Raises:
        SaltinoRuntimeError: Se ci sono errori durante l'esecuzione
        Exception: Se ci sono errori di parsing
    """
    interpreter = OptimizedSaltinoInterpreter(
        enable_tail_recursive_optimization=use_optimizations)
    result = interpreter.exec_string(source_code)

    if show_stats:
        interpreter.print_optimization_report()

    return result


def exec_saltino_file(file_path: str, use_optimizations: bool = True, show_stats: bool = False) -> Any:
    """
    Esegue un file Saltino (.salt) con ottimizzazioni opzionali.

    Funzione compatibile con l'interprete originale.

    Args:
        file_path: Il percorso del file da eseguire
        use_optimizations: Se True applica le trasformazioni AST (default: True)
        show_stats: Se True mostra statistiche sulle trasformazioni (default: False)

    Returns:
        Any: Il risultato dell'esecuzione del programma

    Raises:
        FileNotFoundError: Se il file non esiste
        SaltinoRuntimeError: Se ci sono errori durante l'esecuzione
        Exception: Se ci sono errori di parsing
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        return exec_saltino(source_code, use_optimizations, show_stats)

    except FileNotFoundError:
        raise FileNotFoundError(f"File non trovato: {file_path}")


def run_program_from_directory(program_name: str, programs_dir: str = 'programs', use_optimizations: bool = True, show_stats: bool = False, verbose: bool = False) -> Any:
    """
    Esegue un programma dalla directory specificata.

    Args:
        program_name: Il nome del programma (con o senza estensione .salt)
        programs_dir: Directory contenente i programmi (default: 'programs')
        use_optimizations: Se True applica le trasformazioni AST (default: True)
        show_stats: Se True mostra statistiche sulle trasformazioni (default: False)
        verbose: Se True mostra informazioni dettagliate (default: False)

    Returns:
        Any: Il risultato dell'esecuzione del programma
    """
    # Aggiungi estensione se mancante
    if not program_name.endswith('.salt'):
        program_name += '.salt'

    # Costruisci il percorso completo
    program_path = os.path.join(programs_dir, program_name)

    if not os.path.exists(program_path):
        raise FileNotFoundError(f"Programma non trovato: {program_path}")

    if verbose:
        print(f"Eseguendo programma: {program_name}")
        if use_optimizations:
            print("(con trasformazioni AST abilitate)")
        else:
            print("(con trasformazioni AST disabilitate)")
        print()

    result = exec_saltino_file(program_path, use_optimizations, show_stats)

    if verbose:
        print(f"Risultato: {result}")

    return result


def list_programs(programs_dir: str = 'programs') -> List[str]:
    """
    Lista tutti i programmi disponibili nella directory specificata.

    Args:
        programs_dir: Directory da controllare (default: 'programs')

    Returns:
        List[str]: Lista dei nomi dei file .salt
    """
    if not os.path.exists(programs_dir):
        return []

    programs = []
    for file in os.listdir(programs_dir):
        if file.endswith('.salt'):
            programs.append(file)

    return sorted(programs)


def run_all_programs(programs_dir: str = 'programs', use_optimizations: bool = True, show_stats: bool = False) -> Dict[str, Any]:
    """
    Esegue tutti i programmi nella directory specificata.

    Args:
        programs_dir: Directory contenente i programmi (default: 'programs')
        use_optimizations: Se True applica le trasformazioni AST (default: True)
        show_stats: Se True mostra statistiche sulle trasformazioni (default: False)

    Returns:
        Dict[str, Any]: Dizionario con i risultati di ogni programma
    """
    programs = list_programs(programs_dir)
    results = {}

    for program in programs:
        print(f"\n{'='*50}")
        print(f"Eseguendo {program}")
        print('='*50)

        try:
            result = run_program_from_directory(
                program,
                programs_dir,
                use_optimizations=use_optimizations,
                show_stats=show_stats
            )
            results[program] = result
            print(f"Risultato: {result}")

        except Exception as e:
            print(f"Errore in {program}: {e}")
            results[program] = f"ERRORE: {e}"

    return results


# ==================== MAIN ====================

def main():
    """Funzione principale per eseguire l'interprete da linea di comando."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Optimized Saltino Interpreter')
    parser.add_argument('file', nargs='?', help='File .salt to execute')
    parser.add_argument('--list', action='store_true',
                        help='List all programs in programs/ directory')
    parser.add_argument('--all', action='store_true',
                        help='Run all programs in programs/ directory')
    parser.add_argument('--no-opt', action='store_true',
                        help='Disable AST transformations')
    parser.add_argument('--stats', action='store_true',
                        help='Show transformation statistics')
    parser.add_argument('--demo', action='store_true',
                        help='Run transformation demo')

    args = parser.parse_args()

    use_optimizations = not args.no_opt

    try:
        if args.demo:
            from transformation_demo import run_demo
            run_demo()
            return

        if args.list:
            programs = list_programs('programs')
            print("Programmi disponibili:")
            for program in programs:
                print(f"  - {program}")
            return

        if args.all:
            results = run_all_programs(
                'programs', use_optimizations=use_optimizations, show_stats=args.stats)
            print(f"\n{'='*50}")
            print("RIEPILOGO")
            print('='*50)
            for program, result in results.items():
                print(f"{program}: {result}")
            return

        if not args.file:
            print("Usage: python optimized_interpreter.py <file.salt>")
            print("       python optimized_interpreter.py --list")
            print("       python optimized_interpreter.py --all")
            print("       python optimized_interpreter.py --demo")
            sys.exit(1)

        # Esegui il file specificato
        result = exec_saltino_file(
            args.file, use_optimizations=use_optimizations, show_stats=args.stats)
        print(f"Risultato programma: {result}")

    except FileNotFoundError as e:
        print(f"Errore: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"Errore: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
