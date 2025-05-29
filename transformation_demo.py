"""
Demo completa delle trasformazioni tail-recursive.

Questo modulo dimostra come utilizzare il sistema di trasformazione
per convertire funzioni ricorsive in forma tail-recursive.
"""

from transformation_pipeline import build_transformed_ast, compare_transformations
from AST.ASTNodes import *
import os


def print_function_structure(func: Function, indent: int = 0):
    """Stampa la struttura di una funzione in modo leggibile."""
    ind = "  " * indent
    print(f"{ind}def {func.name}({', '.join(func.parameters)}) {{")
    
    for stmt in func.body.statements:
        print_statement(stmt, indent + 1)
    
    print(f"{ind}}}")


def print_statement(stmt, indent: int = 0):
    """Stampa un statement in modo leggibile."""
    ind = "  " * indent
    
    if isinstance(stmt, ReturnStatement):
        print(f"{ind}return {format_expression(stmt.value)}")
    elif isinstance(stmt, IfStatement):
        print(f"{ind}if {format_expression(stmt.condition)} {{")
        for s in stmt.then_block.statements:
            print_statement(s, indent + 1)
        print(f"{ind}}} else {{")
        if stmt.else_block:
            for s in stmt.else_block.statements:
                print_statement(s, indent + 1)
        print(f"{ind}}}")
    else:
        print(f"{ind}{type(stmt).__name__}")


def format_expression(expr) -> str:
    """Formatta un'espressione per la stampa."""
    if isinstance(expr, Identifier):
        return expr.name
    elif isinstance(expr, IntegerLiteral):
        return str(expr.value)
    elif isinstance(expr, BinaryExpression):
        return f"({format_expression(expr.left)} {expr.operator} {format_expression(expr.right)})"
    elif isinstance(expr, FunctionCall):
        args = ", ".join(format_expression(arg) for arg in expr.arguments)
        return f"{format_expression(expr.function)}({args})"
    elif isinstance(expr, ComparisonCondition):
        return f"({format_expression(expr.left)} {expr.operator} {format_expression(expr.right)})"
    elif isinstance(expr, IfStatement):
        return f"if {format_expression(expr.condition)} then ... else ..."
    else:
        return f"{type(expr).__name__}"


def demo_factorial_transformation():
    """Dimostra la trasformazione della funzione factorial."""
    
    print("=" * 60)
    print("DEMO: Trasformazione Tail-Recursive della Funzione Factorial")
    print("=" * 60)
    
    factorial_code = """
def factorial(n) {
    if (n <= 1) {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}
"""
    
    print("\n1. CODICE ORIGINALE:")
    print(factorial_code)
    
    # AST originale
    print("2. STRUTTURA AST ORIGINALE:")
    original_ast = build_transformed_ast(factorial_code, apply_tail_recursive=False)
    for func in original_ast.functions:
        print_function_structure(func)
        print()
    
    # AST trasformato
    print("3. STRUTTURA AST TRASFORMATO:")
    transformed_ast = build_transformed_ast(factorial_code, apply_tail_recursive=True)
    for func in transformed_ast.functions:
        print_function_structure(func)
        print()
    
    print("4. SPIEGAZIONE DELLA TRASFORMAZIONE:")
    print("   - La funzione originale 'factorial(n)' diventa un wrapper")
    print("   - Viene creata 'factorial_aux(n, acc)' che è tail-recursive")
    print("   - L'accumulatore mantiene il risultato parziale")
    print("   - Ogni chiamata ricorsiva aggiorna l'accumulatore")
    print("   - Il caso base ritorna direttamente l'accumulatore")


def test_with_real_files():
    """Testa con i file reali del progetto."""
    
    print("\n" + "=" * 60)
    print("TEST CON FILE REALI")
    print("=" * 60)
    
    test_files = ['programs/factorial.salt']
    
    for filepath in test_files:
        if os.path.exists(filepath):
            print(f"\nTestando: {filepath}")
            
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                
                print("Contenuto file:")
                print(content)
                
                # Confronto
                comparison = compare_transformations(filepath)
                
                print(f"Funzioni originali: {comparison['original_functions']}")
                print(f"Funzioni trasformate: {comparison['transformed_functions']}")
                print(f"Trasformazione applicata: {comparison['transformation_applied']}")
                
                if comparison['transformation_applied']:
                    print("\nMostrando AST trasformato:")
                    transformed_ast = build_transformed_ast(content, apply_tail_recursive=True)
                    for func in transformed_ast.functions:
                        print_function_structure(func)
                        print()
                
            except Exception as e:
                print(f"Errore con {filepath}: {e}")
        else:
            print(f"File {filepath} non trovato")


def demo_multiple_functions():
    """Dimostra trasformazione con più funzioni."""
    
    print("\n" + "=" * 60)
    print("DEMO: Programma con Più Funzioni")
    print("=" * 60)
    
    multi_code = """
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

def helper(x) {
    return x + 1
}
"""
    
    print("CODICE ORIGINALE:")
    print(multi_code)
    
    # Analisi
    from transformation_pipeline import analyze_program_recursion
    analysis = analyze_program_recursion(multi_code)
    
    print(f"\nANALISI:")
    print(f"Funzioni totali: {analysis['total_functions']}")
    print(f"Funzioni trasformabili: {analysis['transformable_functions']}")
    
    for detail in analysis['function_details']:
        status = "✓ Trasformabile" if detail['can_transform'] else "✗ Non trasformabile"
        print(f"  - {detail['name']}: {status}")
        if detail['reason']:
            print(f"    Motivo: {detail['reason']}")
        if detail['pattern']:
            print(f"    Pattern: {detail['pattern']}")
    
    # Trasformazione
    print(f"\nTRASFORMAZIONE:")
    transformed_ast = build_transformed_ast(multi_code, apply_tail_recursive=True)
    
    print("Funzioni nel programma trasformato:")
    for func in transformed_ast.functions:
        print(f"  - {func.name}({', '.join(func.parameters)})")


if __name__ == "__main__":
    demo_factorial_transformation()
    demo_multiple_functions()
    test_with_real_files()
