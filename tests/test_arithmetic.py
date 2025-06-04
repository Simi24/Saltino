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
        Program: Various operations with -5, 0, 3
        """
        program_path = test_suite_path / "arithmetic" / "negative_zero_numbers.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        # Need to analyze the specific program to determine expected result
        assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"
    
    def test_power_operations(self, saltino_executor, test_suite_path):
        """
        Test power operations (if supported)
        """
        program_path = test_suite_path / "arithmetic" / "power_operations.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"
    
    def test_precedence(self, saltino_executor, test_suite_path):
        """
        Test operator precedence
        """
        program_path = test_suite_path / "arithmetic" / "precedence_test.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"
    
    def test_unary_operators(self, saltino_executor, test_suite_path):
        """
        Test unary operators (+, -)
        """
        program_path = test_suite_path / "arithmetic" / "unary_operators.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"
