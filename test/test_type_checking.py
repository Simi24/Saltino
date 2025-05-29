#!/usr/bin/env python3
"""
Test per verificare il controllo dei tipi nell'interprete iterativo Saltino.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from iterative_interpreter import IterativeSaltinoInterpreter, SaltinoRuntimeError
from AST.ASTNodes import *

def test_arithmetic_type_checking():
    """Test controllo tipi per operatori aritmetici."""
    print("Testing arithmetic type checking...")
    
    interpreter = IterativeSaltinoInterpreter()
    
    # Test operazione aritmetica valida (int + int)
    try:
        result = interpreter._arithmetic_op(5, 3, lambda x, y: x + y)
        assert result == 8
        print("✓ Valid arithmetic operation (int + int) works")
    except Exception as e:
        print(f"✗ Valid arithmetic operation failed: {e}")
    
    # Test operazione aritmetica non valida (string + int)
    try:
        interpreter._arithmetic_op("hello", 3, lambda x, y: x + y)
        print("✗ Invalid arithmetic operation (string + int) should have failed")
    except SaltinoRuntimeError as e:
        print("✓ Invalid arithmetic operation correctly rejected")
    
    # Test operazione aritmetica non valida (bool + int)
    try:
        interpreter._arithmetic_op(True, 3, lambda x, y: x + y)
        print("✗ Invalid arithmetic operation (bool + int) should have failed")
    except SaltinoRuntimeError as e:
        print("✓ Invalid arithmetic operation correctly rejected")

def test_cons_type_checking():
    """Test controllo tipi per operatore cons."""
    print("\nTesting cons operator type checking...")
    
    interpreter = IterativeSaltinoInterpreter()
    
    # Test cons valido (int :: [int])
    try:
        result = interpreter._cons(5, [1, 2, 3])
        assert result == [5, 1, 2, 3]
        print("✓ Valid cons operation (int :: [int]) works")
    except Exception as e:
        print(f"✗ Valid cons operation failed: {e}")
    
    # Test cons con lista vuota
    try:
        result = interpreter._cons(5, [])
        assert result == [5]
        print("✓ Valid cons operation (int :: []) works")
    except Exception as e:
        print(f"✗ Valid cons operation failed: {e}")
    
    # Test cons non valido (string :: [int])
    try:
        interpreter._cons("hello", [1, 2, 3])
        print("✗ Invalid cons operation (string :: [int]) should have failed")
    except SaltinoRuntimeError as e:
        print("✓ Invalid cons operation correctly rejected")
    
    # Test cons non valido (int :: string)
    try:
        interpreter._cons(5, "hello")
        print("✗ Invalid cons operation (int :: string) should have failed")
    except SaltinoRuntimeError as e:
        print("✓ Invalid cons operation correctly rejected")
    
    # Test cons non valido (int :: [string])
    try:
        interpreter._cons(5, ["hello", "world"])
        print("✗ Invalid cons operation (int :: [string]) should have failed")
    except SaltinoRuntimeError as e:
        print("✓ Invalid cons operation correctly rejected")

def test_comparison_type_checking():
    """Test controllo tipi per operatori di confronto."""
    print("\nTesting comparison operators type checking...")
    
    interpreter = IterativeSaltinoInterpreter()
    
    # Test confronto valido (int < int)
    try:
        result = interpreter._comparison_op(5, 3, lambda x, y: x > y)
        assert result == True
        print("✓ Valid comparison operation (int > int) works")
    except Exception as e:
        print(f"✗ Valid comparison operation failed: {e}")
    
    # Test confronto non valido (string < int)
    try:
        interpreter._comparison_op("hello", 3, lambda x, y: x < y)
        print("✗ Invalid comparison operation (string < int) should have failed")
    except SaltinoRuntimeError as e:
        print("✓ Invalid comparison operation correctly rejected")

def test_equality_type_checking():
    """Test controllo tipi per operatore di uguaglianza."""
    print("\nTesting equality operator type checking...")
    
    interpreter = IterativeSaltinoInterpreter()
    
    # Test uguaglianza valida (int == int)
    try:
        result = interpreter._equality_comparison(5, 5)
        assert result == True
        print("✓ Valid equality operation (int == int) works")
    except Exception as e:
        print(f"✗ Valid equality operation failed: {e}")
    
    # Test uguaglianza valida ([] == [])
    try:
        result = interpreter._equality_comparison([], [])
        assert result == True
        print("✓ Valid equality operation ([] == []) works")
    except Exception as e:
        print(f"✗ Valid equality operation failed: {e}")
    
    # Test uguaglianza valida ([int] == [])
    try:
        result = interpreter._equality_comparison([1, 2], [])
        assert result == False
        print("✓ Valid equality operation ([int] == []) works")
    except Exception as e:
        print(f"✗ Valid equality operation failed: {e}")
    
    # Test uguaglianza non valida ([int] == [int] con entrambe non vuote)
    try:
        interpreter._equality_comparison([1, 2], [3, 4])
        print("✗ Invalid equality operation ([int] == [int]) should have failed")
    except SaltinoRuntimeError as e:
        print("✓ Invalid equality operation correctly rejected")

def test_logical_type_checking():
    """Test controllo tipi per connettivi logici."""
    print("\nTesting logical operators type checking...")
    
    interpreter = IterativeSaltinoInterpreter()
    
    # Test operazione logica valida (bool and bool)
    try:
        result = interpreter._logical_op(True, False, lambda x, y: x and y)
        assert result == False
        print("✓ Valid logical operation (bool and bool) works")
    except Exception as e:
        print(f"✗ Valid logical operation failed: {e}")
    
    # Test operazione logica non valida (int and bool)
    try:
        interpreter._logical_op(1, True, lambda x, y: x and y)
        print("✗ Invalid logical operation (int and bool) should have failed")
    except SaltinoRuntimeError as e:
        print("✓ Invalid logical operation correctly rejected")
    
    # Test operazione logica non valida (bool and string)
    try:
        interpreter._logical_op(True, "hello", lambda x, y: x and y)
        print("✗ Invalid logical operation (bool and string) should have failed")
    except SaltinoRuntimeError as e:
        print("✓ Invalid logical operation correctly rejected")

def main():
    """Esegue tutti i test."""
    print("=== Testing Saltino Type Checking ===")
    
    test_arithmetic_type_checking()
    test_cons_type_checking()
    test_comparison_type_checking()
    test_equality_type_checking()
    test_logical_type_checking()
    
    print("\n=== Type checking tests completed ===")

if __name__ == "__main__":
    main()
