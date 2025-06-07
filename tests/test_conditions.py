"""
Test suite for conditional statements in Saltino
"""
import pytest
from pathlib import Path

@pytest.mark.conditions
class TestConditions:
    
    def test_boolean_literal(self, saltino_executor, test_suite_path):
        """
        Test simple boolean literals in conditions
        Program logic:
        - if (true): return 1 else: return 0
        Expected: 1
        """
        program_path = test_suite_path / "conditions" / "boolean_literal.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 1, f"Expected 1, got {result}"
    
    def test_boolean_complete(self, saltino_executor, test_suite_path):
        """
        Test boolean variables with logical operators
        Program logic:
        - a = true, b = false
        - if (a and !b): return 42 else: return 0
        Expected: 42
        """
        program_path = test_suite_path / "conditions" / "test_boolean_complete.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 42, f"Expected 42, got {result}"
    
    def test_simple_comparison(self, saltino_executor, test_suite_path):
        """
        Test simple comparison operators
        Program logic:
        - a = 10, b = 5
        - if (a > b): return 1 else: return 0
        Expected: 1
        """
        program_path = test_suite_path / "conditions" / "simple_comparison.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 1, f"Expected 1, got {result}"
    
    def test_boolean_variables(self, saltino_executor, test_suite_path):
        """
        Test boolean variables using auxiliary functions
        Program logic:
        - test_true_variable() returns 1 (true_val = true, if true_val)
        - test_false_variable() returns 1 (false_val = false, else branch)
        - return 1 + 1 = 2
        Expected: 2
        """
        program_path = test_suite_path / "conditions" / "boolean_variables.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 2, f"Expected 2, got {result}"
    
    def test_comparison_operators(self, saltino_executor, test_suite_path):
        """
        Test comparison operators using auxiliary functions
        Program logic: a=10, b=5, c=10
        - test_greater(a, b) returns 1 (10>5 true)
        - test_greater_equal(a, c) returns 1 (10>=10 true)  
        - test_less(b, a) returns 1 (5<10 true)
        - test_equal(a, c) returns 1 (10==10 true)
        - return 1 + 1 + 1 + 1 = 4
        Expected: 4
        """
        program_path = test_suite_path / "conditions" / "comparison_operators.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 4, f"Expected 4, got {result}"
    
    def test_logical_operators(self, saltino_executor, test_suite_path):
        """
        Test logical operators using auxiliary functions
        Program logic:
        - test_and(true, true) returns 1
        - test_or(false, true) returns 1
        - test_not(false) returns 1
        - test_and(true, false) returns 0
        - return 1 + 1 + 1 + 0 = 3
        Expected: 3
        """
        program_path = test_suite_path / "conditions" / "logical_operators.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 3, f"Expected 3, got {result}"
    
    def test_logical_precedence(self, saltino_executor, test_suite_path):
        """
        Test logical operator precedence using auxiliary functions
        Program logic:
        - test_precedence1() returns 1 (true or false and false = true)
        - test_precedence2() returns 1 (false and true or true = true)
        - test_negation() returns 1 (!false and true = true)
        - test_negation_or() returns 1 (!true or false = false, else branch)
        - return 1 + 1 + 1 + 1 = 4
        Expected: 4
        """
        program_path = test_suite_path / "conditions" / "logical_precedence.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 4, f"Expected 4, got {result}"
        
    def test_list_comparison(self, saltino_executor, test_suite_path):
        """
        Test list comparison operators using auxiliary functions
        Program logic:
        - test_empty_equals() returns 1 ([] == [] is true)
        - test_non_empty_vs_empty() returns 1 (non_empty != [], else branch)
        - test_empty_vs_non_empty() returns 1 ([] != non_empty, else branch)
        - return 1 + 1 + 1 = 3
        Expected: 3
        """
        program_path = test_suite_path / "conditions" / "list_comparison.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 3, f"Expected 3, got {result}"
    
    def test_complex_conditions(self, saltino_executor, test_suite_path):
        """
        Test complex conditional expressions using auxiliary functions
        Program logic:
        - test_complex1() returns 1 ((10 > 5) and (15 > 10) = true)
        - test_complex2() returns 1 ((3 == 3) or (7 < 3) = true)
        - test_complex3() returns 1 (true and !false = true)
        - test_complex4() returns 1 (!(8 > 12) and (8 < 12) = true)
        - return 1 + 1 + 1 + 1 = 4
        Expected: 4
        """
        program_path = test_suite_path / "conditions" / "complex_conditions.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 4, f"Expected 4, got {result}"
