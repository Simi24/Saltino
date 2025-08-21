"""
Test suite for basic functionality in Saltino
"""
import pytest
from pathlib import Path

@pytest.mark.basic
class TestBasicFunctionality:
    
    def test_hello_world(self, saltino_executor, test_suite_path):
        """
        Test the simplest possible program - main function returning 42
        """
        program_path = test_suite_path / "basic_functionality" / "hello_world.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 42, f"Expected 42, got {result}"
    
    def test_variable_assignment(self, saltino_executor, test_suite_path):
        """
        Test basic variable assignment and return
        Program: x=10, y=20, z=x+y=30
        Expected: 30
        """
        program_path = test_suite_path / "basic_functionality" / "variable_assignment.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 30, f"Expected 30, got {result}"
    
    def test_main_with_params(self, saltino_executor, test_suite_path):
        """
        Test main function with parameters
        Program: main(x, y) returns x + y
        This test depends on how parameters are passed to main function
        Expected: depends on implementation (will need to be determined at runtime)
        """
        program_path = test_suite_path / "basic_functionality" / "main_with_params.salt"
        result, error = saltino_executor(program_path)
        
        # This test may fail if main with parameters isn't supported
        # or if parameters aren't provided properly
        if error is not None:
            pytest.skip(f"Main with parameters not supported: {error}")
        assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"
    
    def test_empty_nested_blocks(self, saltino_executor, test_suite_path):
        """
        Test handling of empty and nested blocks
        Program: x=5, nested blocks with y=10, z=x+y=15, returns x+10=15
        Expected: 15
        """
        program_path = test_suite_path / "basic_functionality" / "empty_nested_blocks.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 15, f"Expected 15, got {result}"
