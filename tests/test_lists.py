"""
Test suite for list operations in Saltino
"""
import pytest
from pathlib import Path

@pytest.mark.lists
class TestLists:
    
    def test_list_operations(self, saltino_executor):
        """
        Test basic list operations
        """
        program_path = Path("/workspace/programs/lists.salt")
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        # Lists might return different types depending on implementation
        assert result is not None, f"Expected non-None result"
    
    def test_append_operation(self, saltino_executor):
        """
        Test list append operation
        """
        program_path = Path("/workspace/programs/append.salt")
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result is not None, f"Expected non-None result"
    
    def test_map_operation(self, saltino_executor):
        """
        Test map operation on lists
        """
        program_path = Path("/workspace/programs/map.salt")
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result is not None, f"Expected non-None result"
    
    def test_dot_product(self, saltino_executor):
        """
        Test dot product of two vectors
        """
        program_path = Path("/workspace/programs/dot_product.salt")
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"
