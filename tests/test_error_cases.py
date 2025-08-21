"""
Test suite for error cases in Saltino
"""
import pytest
from pathlib import Path

@pytest.mark.error_cases
class TestErrorCases:
    
    def test_division_by_zero(self, saltino_executor, test_suite_path):
        """
        Test that division by zero is handled appropriately
        Program: x=10, y=0, return x/y
        Expected: Should generate runtime error
        """
        program_path = test_suite_path / "error_cases" / "division_by_zero.salt"
        result, error = saltino_executor(program_path)
        
        # Should error for division by zero
        assert error is not None, "Expected error for division by zero"
    
    def test_undefined_variable(self, saltino_executor, test_suite_path):
        """
        Test undefined variable access
        Program: x=10, return y (y is undefined)
        Expected: Should generate error for undefined variable
        """
        program_path = test_suite_path / "error_cases" / "undefined_variable.salt"
        result, error = saltino_executor(program_path)
        
        # Should definitely error for undefined variable
        assert error is not None, "Expected error for undefined variable access"
    
    def test_type_mismatch(self, saltino_executor, test_suite_path):
        """
        Test type mismatch errors
        """
        program_path = test_suite_path / "error_cases" / "type_mismatch.salt"
        
        if not program_path.exists():
            pytest.skip("Type mismatch test file not found")
        
        result, error = saltino_executor(program_path)
        
        # Should error for type mismatches
        assert error is not None, "Expected error for type mismatch"

    def test_head_empty_list(self, saltino_executor, test_suite_path):
        """
        Test head operation on empty list
        Expected: Should generate runtime error
        """
        program_path = test_suite_path / "error_cases" / "head_empty_list.salt"
        result, error = saltino_executor(program_path)
        
        assert error is not None, "Expected error for head on empty list"

    def test_undefined_function(self, saltino_executor, test_suite_path):
        """
        Test calling undefined function
        Expected: Should generate error for undefined function
        """
        program_path = test_suite_path / "error_cases" / "undefined_function.salt"
        result, error = saltino_executor(program_path)
        
        assert error is not None, "Expected error for undefined function call"

    def test_wrong_parameter_count(self, saltino_executor, test_suite_path):
        """
        Test calling function with wrong number of parameters
        Expected: Should generate error for parameter count mismatch
        """
        program_path = test_suite_path / "error_cases" / "wrong_parameter_count.salt"
        result, error = saltino_executor(program_path)
        
        assert error is not None, "Expected error for wrong parameter count"

    def test_modulo_by_zero(self, saltino_executor, test_suite_path):
        """
        Test modulo by zero
        Expected: Should generate runtime error
        """
        program_path = test_suite_path / "error_cases" / "modulo_by_zero.salt"
        result, error = saltino_executor(program_path)
        
        assert error is not None, "Expected error for modulo by zero"
