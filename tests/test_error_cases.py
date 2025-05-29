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
        """
        # Create a simple division by zero test
        program_content = """
def main() {
    a = 10
    b = 0
    return a / b
}
"""
        # For now, we expect this to either:
        # 1. Raise an exception (error != None)
        # 2. Return some error value like infinity
        program_path = test_suite_path / "error_cases" / "division_by_zero.salt"
        
        # We might need to create this file if it doesn't exist
        if not program_path.exists():
            pytest.skip("Division by zero test file not found")
        
        result, error = saltino_executor(program_path)
        
        # Either should error or handle gracefully
        if error is None:
            # If no error, result should indicate the issue somehow
            assert result != 10, "Division by zero should not return normal result"
    
    def test_undefined_variable(self, saltino_executor, test_suite_path):
        """
        Test undefined variable access
        """
        program_path = test_suite_path / "error_cases" / "undefined_variable.salt"
        
        if not program_path.exists():
            pytest.skip("Undefined variable test file not found")
        
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
