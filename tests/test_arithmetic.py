"""
Test suite for arithmetic operations in Saltino
"""
import pytest
from pathlib import Path

@pytest.mark.arithmetic
class TestArithmeticOperations:
    
    def test_basic_operations(self, saltino_executor, test_suite_path):
        """
        Test basic arithmetic operations: +, -, *, /, %
        Program: a=15, b=4
        Expected: sum(19) + diff(11) + prod(60) + div(3) + mod(3) = 96
        Note: Division is integer division (//)
        """
        program_path = test_suite_path / "arithmetic" / "basic_operations.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 96, f"Expected 96, got {result}"
    
    def test_negative_zero_operations(self, saltino_executor, test_suite_path):
        """
        Test operations with negative numbers and zero
        Program: zero=0, negative=-42, positive=42
        result1 = 0 + (-42) = -42
        result2 = -42 + 42 = 0
        result3 = 0 * 100 = 0
        result4 = -42 / -42 = 1
        Expected: -42 + 0 + 0 + 1 = -41
        """
        program_path = test_suite_path / "arithmetic" / "negative_zero_numbers.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == -41, f"Expected -41, got {result}"
    
    def test_power_operations(self, saltino_executor, test_suite_path):
        """
        Test power operations (^ is right-associative)
        Program: 
        result1 = 2^3^2 = 2^(3^2) = 2^9 = 512
        result2 = (2^3)^2 = 8^2 = 64
        result3 = 2 + 3^2 = 2 + 9 = 11
        Expected: 512 + 64 + 11 = 587
        """
        program_path = test_suite_path / "arithmetic" / "power_operations.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 587, f"Expected 587, got {result}"
    
    def test_precedence(self, saltino_executor, test_suite_path):
        """
        Test operator precedence
        Program:
        result1 = 2 + 3 * 4 = 2 + 12 = 14
        result2 = (2 + 3) * 4 = 5 * 4 = 20
        result3 = 10 - 6 / 2 = 10 - 3 = 7
        result4 = 15 % 4 + 2 = 3 + 2 = 5
        Expected: 14 + 20 + 7 + 5 = 46
        """
        program_path = test_suite_path / "arithmetic" / "precedence_test.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 46, f"Expected 46, got {result}"
    
    def test_unary_operators(self, saltino_executor, test_suite_path):
        """
        Test unary operators (+, -)
        Program: x=10, y=-x=-10, z=+15=15, w=-(-y)=-(-(-10))=-(10)=-10
        Expected: z + w = 15 + (-10) = 5
        """
        program_path = test_suite_path / "arithmetic" / "unary_operators.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 5, f"Expected 5, got {result}"
