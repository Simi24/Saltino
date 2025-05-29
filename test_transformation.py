"""
Test per verificare il parsing e la trasformazione del codice factorial.
"""

from transformation_pipeline import build_ast, analyze_program_recursion
from AST.ASTNodes import *

def test_simple_factorial():
    """Test con codice factorial semplificato."""
    
    # Versione semplificata che dovrebbe funzionare
    factorial_code = """
def factorial(n) {
    if (n <= 1) {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}
"""
    
    print("=== Test Parsing Factorial ===")
    
    try:
        # Prova a parsare
        ast = build_ast(factorial_code)
        print(f"Parsing riuscito: {len(ast.functions)} funzioni")
        
        # Esamina la struttura
        factorial_func = ast.functions[0]
        print(f"Funzione: {factorial_func.name}")
        print(f"Parametri: {factorial_func.parameters}")
        print(f"Statements nel body: {len(factorial_func.body.statements)}")
        
        # Esamina il primo statement
        first_stmt = factorial_func.body.statements[0]
        print(f"Primo statement: {type(first_stmt).__name__}")
        
        if isinstance(first_stmt, ReturnStatement):
            print(f"Return value type: {type(first_stmt.value).__name__}")
            
            if isinstance(first_stmt.value, IfStatement):
                print("Il return contiene un if-statement!")
                if_stmt = first_stmt.value
                print(f"Condition type: {type(if_stmt.condition).__name__}")
                print(f"Then block statements: {len(if_stmt.then_block.statements)}")
                if if_stmt.else_block:
                    print(f"Else block statements: {len(if_stmt.else_block.statements)}")
        
        # Test di analisi
        print("\n=== Analisi Ricorsione ===")
        analysis = analyze_program_recursion(factorial_code)
        print(f"Funzioni trasformabili: {analysis['transformable_functions']}")
        
        for detail in analysis['function_details']:
            print(f"- {detail['name']}: {detail['can_transform']}")
            if detail['reason']:
                print(f"  Motivo: {detail['reason']}")
                
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()

def test_main_function():
    """Test della funzione main."""
    
    main_code = """
def main() {
    return factorial(5)
}
"""
    
    print("\n=== Test Parsing Main ===")
    
    try:
        ast = build_ast(main_code)
        main_func = ast.functions[0]
        print(f"Funzione: {main_func.name}")
        print(f"Parametri: {main_func.parameters} (count: {len(main_func.parameters)})")
        
    except Exception as e:
        print(f"Errore: {e}")

def test_actual_transformation():
    """Test della trasformazione effettiva."""
    
    factorial_code = """
def factorial(n) {
    if (n <= 1) {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}
"""
    
    print("\n=== Test Trasformazione ===")
    
    try:
        from transformation_pipeline import build_transformed_ast
        
        # AST originale
        original_ast = build_transformed_ast(factorial_code, apply_tail_recursive=False)
        print(f"Funzioni originali: {len(original_ast.functions)}")
        for func in original_ast.functions:
            print(f"  - {func.name}({', '.join(func.parameters)})")
        
        # AST trasformato
        transformed_ast = build_transformed_ast(factorial_code, apply_tail_recursive=True)
        print(f"Funzioni trasformate: {len(transformed_ast.functions)}")
        for func in transformed_ast.functions:
            print(f"  - {func.name}({', '.join(func.parameters)})")
            
        print("\nTrasformazione riuscita!")
        
    except Exception as e:
        print(f"Errore durante trasformazione: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_factorial()
    test_main_function()
    test_actual_transformation()
    test_actual_transformation()
