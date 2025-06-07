"""
Test suite for conditional statements in Saltino
"""
import pytest
from pathlib import Path

@pytest.mark.conditions
class TestConditions:
    
    def test_boolean_variables(self, saltino_executor, test_suite_path):
        """
        Test boolean logic using boolean literals
        Program logic:
        - true_val = true, false_val = false
        - if (true_val): result += 1  -> result = 1  
        - if (false_val): result += 100 else: result += 1  -> result = 2
        Expected: 2
        """
        program_path = test_suite_path / "conditions" / "boolean_variables.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 2, f"Expected 2, got {result}"
    
    def test_comparison_operators(self, saltino_executor, test_suite_path):
        """
        Test comparison operators: ==, !=, <, >, <=, >=
        Program: a=10, b=5, c=10
        - if (a > b): result += 1  -> result = 1 (10>5 true)
        - if (a >= c): result += 1  -> result = 2 (10>=10 true)  
        - if (b < a): result += 1  -> result = 3 (5<10 true)
        - if (c <= a): result += 1  -> result = 4 (10<=10 true)
        - if (a == c): result += 1  -> result = 5 (10==10 true)
        Expected: 5
        """
        program_path = test_suite_path / "conditions" / "comparison_operators.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 5, f"Expected 5, got {result}"
    
    def test_complex_conditions(self, saltino_executor, test_suite_path):
        """
        Test complex conditional expressions with logical operators
        Program: a=5, b=10, c=15
        - if ((a < b) and (b < c)): result += 1  -> result = 1 (true and true)
        - if ((a > b) or (c > b)): result += 1  -> result = 2 (false or true)
        - if (!(a == b) and (c > a)): result += 1  -> result = 3 (true and true)
        - if (((a + b) > c) or ((a * 2) == b)): result += 1  -> result = 4 (false or true)
        Expected: 4
        """
        program_path = test_suite_path / "conditions" / "complex_conditions.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 4, f"Expected 4, got {result}"
