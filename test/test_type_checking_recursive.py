#!/usr/bin/env python3
"""
Test dei controlli di tipo per l'interprete ricorsivo di Saltino.
"""

from interpreter import exec_saltino, SaltinoRuntimeError


def test_type_checking_recursive():
    """Test completo dei controlli di tipo per l'interprete ricorsivo."""

    print("=== Testing Saltino Type Checking (Recursive Interpreter) ===")

    # Test 1: Operatori aritmetici
    print("Testing arithmetic type checking...")

    # Test valido
    try:
        result = exec_saltino("""
def main() {
    return 5 + 3
}
""")
        print("✓ Valid arithmetic operation (int + int) works")
    except Exception as e:
        print(f"✗ Valid arithmetic operation failed: {e}")

    # Test invalido - cons con numero invece di lista
    try:
        result = exec_saltino("""
def main() {
    return 5 :: 3
}
""")
        print("✗ Invalid cons operation should have failed")
    except SaltinoRuntimeError as e:
        if "Cons operator expects a list" in str(e):
            print("✓ Invalid cons operation correctly rejected")
        else:
            print(f"✗ Wrong error message: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Test 2: Operatore cons
    print("Testing cons operator type checking...")

    # Test valido - cons con intero e lista vuota
    try:
        result = exec_saltino("""
def main() {
    return 5 :: []
}
""")
        print("✓ Valid cons operation (int :: []) works")
    except Exception as e:
        print(f"✗ Valid cons operation failed: {e}")

    # Test valido - cons con intero e lista di interi
    try:
        result = exec_saltino("""
def main() {
    x = 3 :: []
    return 5 :: x
}
""")
        print("✓ Valid cons operation (int :: [int]) works")
    except Exception as e:
        print(f"✗ Valid cons operation failed: {e}")

    # Test 3: Operatori di confronto
    print("Testing comparison operators type checking...")

    # Test valido
    try:
        result = exec_saltino("""
def main() {
    return 5 > 3
}
""")
        print("✓ Valid comparison operation (int > int) works")
    except Exception as e:
        print(f"✗ Valid comparison operation failed: {e}")

    # Test 4: Operatore di uguaglianza
    print("Testing equality operator type checking...")

    # Test valido - confronto tra interi
    try:
        result = exec_saltino("""
def main() {
    return 5 == 3
}
""")
        print("✓ Valid equality operation (int == int) works")
    except Exception as e:
        print(f"✗ Valid equality operation failed: {e}")

    # Test valido - confronto liste vuote
    try:
        result = exec_saltino("""
def main() {
    return [] == []
}
""")
        print("✓ Valid equality operation ([] == []) works")
    except Exception as e:
        print(f"✗ Valid equality operation failed: {e}")

    # Test valido - confronto lista con lista vuota
    try:
        result = exec_saltino("""
def main() {
    x = 5 :: []
    return x == []
}
""")
        print("✓ Valid equality operation ([int] == []) works")
    except Exception as e:
        print(f"✗ Valid equality operation failed: {e}")

    print("=== Type checking tests completed ===")


if __name__ == "__main__":
    test_type_checking_recursive()
