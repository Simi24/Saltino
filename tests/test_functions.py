"""
Test suite for function definitions and calls in Saltino
"""
import pytest
from pathlib import Path

@pytest.mark.functions
class TestFunctions:
    
    def test_factorial(self, saltino_executor):
        """
        Test factorial function
        Expected: factorial(5) = 5! = 5*4*3*2*1 = 120
        """
        program_path = Path("/workspace/programs/factorial.salt")
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 120, f"Expected 120 (5!), got {result}"
    
    def test_fibonacci(self, saltino_executor):
        """
        Test fibonacci function
        Expected: fibonacci(10) = 55
        (0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55)
        """
        program_path = Path("/workspace/programs/fibonacci.salt")
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 55, f"Expected 55 (fibonacci(10)), got {result}"
    
    def test_compose_function(self, saltino_executor):
        """
        Test function composition
        """
        program_path = Path("/workspace/programs/compose.salt")
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"
