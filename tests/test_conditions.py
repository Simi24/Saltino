"""
Test suite for conditional statements in Saltino
"""
import pytest
from pathlib import Path

@pytest.mark.conditions
class TestConditions:
    
    def test_boolean_variables(self, saltino_executor, test_suite_path):
        """
        Test boolean logic using numeric comparisons
        Program logic:
        - true_val = 1, false_val = 0
        - if (true_val == 1): result += 1  -> result = 1
        - if (false_val == 1): result += 100 else: result += 1  -> result = 2
        Expected: 2
        """
        program_path = test_suite_path / "conditions" / "boolean_variables.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 2, f"Expected 2, got {result}"
    
    def test_comparison_operators(self, saltino_executor, test_suite_path):
        """
        Test comparison operators: ==, !=, <, >, <=, >=
        """
        program_path = test_suite_path / "conditions" / "comparison_operators.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"
    
    def test_complex_conditions(self, saltino_executor, test_suite_path):
        """
        Test complex conditional expressions with logical operators
        """
        program_path = test_suite_path / "conditions" / "complex_conditions.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"
