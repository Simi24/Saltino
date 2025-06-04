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
        """
        program_path = test_suite_path / "basic_functionality" / "variable_assignment.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"
    
    def test_main_with_params(self, saltino_executor, test_suite_path):
        """
        Test main function with parameters (if supported)
        """
        program_path = test_suite_path / "basic_functionality" / "main_with_params.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"
    
    def test_empty_nested_blocks(self, saltino_executor, test_suite_path):
        """
        Test handling of empty and nested blocks
        """
        program_path = test_suite_path / "basic_functionality" / "empty_nested_blocks.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"
