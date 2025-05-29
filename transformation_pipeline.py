"""
Pipeline di trasformazione che integra il parser esistente con il trasformatore tail-recursive.

Questo modulo fornisce una interfaccia semplice per:
1. Parsare il codice sorgente in AST
2. Applicare trasformazioni tail-recursive  
3. Ritornare l'AST trasformato pronto per l'interprete
"""

from Grammatica.SaltinoParser import SaltinoParser
from Grammatica.SaltinoLexer import SaltinoLexer
from AST.ASTVisitor import build_ast as ast_build_ast
from AST.ASTNodes import Program
from tail_recursive_transformer import TailRecursiveTransformer
from antlr4 import InputStream, CommonTokenStream
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def build_ast(input_text: str) -> Program:
    """
    Costruisce un AST dal codice sorgente.
    
    Args:
        input_text: Il codice sorgente da parsare
        
    Returns:
        L'AST del programma
    """
    # Crea lo stream di input
    input_stream = InputStream(input_text)
    
    # Crea il lexer
    lexer = SaltinoLexer(input_stream)
    
    # Crea lo stream di token
    token_stream = CommonTokenStream(lexer)
    
    # Crea il parser
    parser = SaltinoParser(token_stream)
    
    # Parsa il programma
    tree = parser.programma()
    
    # Usa la funzione esistente per costruire l'AST
    ast = ast_build_ast(tree)
    
    return ast


def build_transformed_ast(input_text: str, apply_tail_recursive: bool = True) -> Program:
    """
    Costruisce un AST trasformato dal codice sorgente.
    
    Args:
        input_text: Il codice sorgente da parsare
        apply_tail_recursive: Se applicare le trasformazioni tail-recursive
        
    Returns:
        L'AST del programma (eventualmente trasformato)
    """
    # Costruisce l'AST base
    ast = build_ast(input_text)
    
    # Applica le trasformazioni se richieste
    if apply_tail_recursive:
        transformer = TailRecursiveTransformer()
        ast = transformer.transform_program(ast)
        
    return ast


def analyze_program_recursion(input_text: str) -> dict:
    """
    Analizza un programma per identificare funzioni ricorsive trasformabili.
    
    Args:
        input_text: Il codice sorgente da analizzare
        
    Returns:
        Dizionario con l'analisi delle funzioni
    """
    ast = build_ast(input_text)
    transformer = TailRecursiveTransformer()
    
    analysis = {
        'total_functions': len(ast.functions),
        'transformable_functions': 0,
        'function_details': []
    }
    
    for function in ast.functions:
        func_analysis = transformer.analyze_function(function)
        analysis['function_details'].append(func_analysis)
        
        if func_analysis['can_transform']:
            analysis['transformable_functions'] += 1
    
    return analysis


def load_and_transform_file(filepath: str, apply_tail_recursive: bool = True) -> Program:
    """
    Carica e trasforma un file .salt.
    
    Args:
        filepath: Percorso del file da caricare
        apply_tail_recursive: Se applicare le trasformazioni tail-recursive
        
    Returns:
        L'AST del programma trasformato
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return build_transformed_ast(content, apply_tail_recursive)


def compare_transformations(filepath: str) -> dict:
    """
    Confronta un programma prima e dopo le trasformazioni.
    
    Args:
        filepath: Percorso del file da analizzare
        
    Returns:
        Dizionario con il confronto
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # AST originale
    original_ast = build_transformed_ast(content, apply_tail_recursive=False)
    
    # AST trasformato  
    transformed_ast = build_transformed_ast(content, apply_tail_recursive=True)
    
    # Analisi
    analysis = analyze_program_recursion(content)
    
    return {
        'original_functions': len(original_ast.functions),
        'transformed_functions': len(transformed_ast.functions),
        'analysis': analysis,
        'transformation_applied': len(transformed_ast.functions) > len(original_ast.functions)
    }


def demo_pipeline():
    """Dimostra l'uso della pipeline di trasformazione."""
    
    # Codice di esempio
    factorial_code = """
def main() {
    return factorial(5)
}

def factorial(n) {
    if (n <= 1) {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}
"""
    
    print("=== Demo Pipeline di Trasformazione ===\n")
    
    # Analisi del programma
    print("1. Analisi del programma:")
    analysis = analyze_program_recursion(factorial_code)
    print(f"   Funzioni totali: {analysis['total_functions']}")
    print(f"   Funzioni trasformabili: {analysis['transformable_functions']}")
    
    for func_detail in analysis['function_details']:
        print(f"   - {func_detail['name']}: {'Trasformabile' if func_detail['can_transform'] else 'Non trasformabile'}")
        if not func_detail['can_transform'] and func_detail['reason']:
            print(f"     Motivo: {func_detail['reason']}")
        if func_detail['pattern']:
            print(f"     Pattern: {func_detail['pattern']}")
    
    print()
    
    # Trasformazione
    print("2. Applicazione delle trasformazioni:")
    transformed_ast = build_transformed_ast(factorial_code, apply_tail_recursive=True)
    
    print(f"   Funzioni dopo trasformazione: {len(transformed_ast.functions)}")
    for func in transformed_ast.functions:
        print(f"   - {func.name}({', '.join(func.parameters)})")
    
    print()
    
    # Test con file reale se disponibile
    test_files = ['programs/factorial.salt', 'programs/fibonacci.salt']
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"3. Test con {test_file}:")
            try:
                comparison = compare_transformations(test_file)
                print(f"   Funzioni originali: {comparison['original_functions']}")
                print(f"   Funzioni trasformate: {comparison['transformed_functions']}")
                print(f"   Trasformazione applicata: {comparison['transformation_applied']}")
                
                analysis = comparison['analysis']
                print(f"   Funzioni trasformabili: {analysis['transformable_functions']}/{analysis['total_functions']}")
                
            except Exception as e:
                print(f"   Errore nel test: {e}")
            print()


if __name__ == "__main__":
    demo_pipeline()
