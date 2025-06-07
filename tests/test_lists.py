"""
Test suite for list operations in Saltino
"""
import pytest

@pytest.mark.lists
class TestLists:
    
    def test_list_operations(self, saltino_executor, test_suite_path):
        """
        Test basic list operations
        Program: Creates empty[], single[1], multiple[1,2,3] lists
        first = head(single) = 1
        rest = tail(multiple) = [2,3]
        second = head(rest) = 2
        Expected: first + second = 1 + 2 = 3
        """
        program_path = test_suite_path / "lists" / "basic_list_operations.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 3, f"Expected 3, got {result}"
    
    def test_append_operation(self, saltino_executor, test_suite_path):
        """
        Test list append operation
        Program: append([1,2], [3,4]) = [1,2,3,4], head([1,2,3,4]) = 1
        Expected: 1
        """
        program_path = test_suite_path / "lists" / "append.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 1, f"Expected 1, got {result}"
    
    def test_cons_operations(self, saltino_executor, test_suite_path):
        """
        Test cons operations and precedence
        Program: Tests operator precedence with cons
        list1 = 1 + 2 :: [] = 3 :: [] -> head = 3
        list2 = 2 * 3 :: 4 :: [] = 6 :: 4 :: [] -> head = 6, second = 4
        Expected: 3 + (6 + 4) = 13
        """
        program_path = test_suite_path / "lists" / "cons_precedence.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 13, f"Expected 13, got {result}"
    
    def test_dot_product(self, saltino_executor, test_suite_path):
        """
        Test dot product of two vectors
        Program: dot_product requires parameters (x1, x2, y1, y2)
        The program expects input parameters, so it will likely error asking for input
        Expected: Error due to missing parameters or stdin reading issue
        """
        program_path = test_suite_path / "lists" / "dot_product.salt"
        result, error = saltino_executor(program_path)
        
        # dot_product requires parameters, should error due to missing input
        assert error is not None, f"Expected error due to missing parameters, but got result: {result}"
    
    def test_nested_head_tail(self, saltino_executor, test_suite_path):
        """
        Test nested head and tail operations
        Program: numbers = [10, 20, 30, 40]
        first = 10, second = 20, third = 30, fourth = 40, middle_two = 30
        Expected: 10 + 20 + 30 + 40 + 30 = 130
        """
        program_path = test_suite_path / "lists" / "nested_head_tail.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 130, f"Expected 130, got {result}"
    
    def test_list_construction(self, saltino_executor, test_suite_path):
        """
        Test basic list construction and operations
        Program: x = [1], y = [2, 1], z = [3, 2, 1]
        head(z) = 3, head(tail(z)) = 2
        Expected: 3 + 2 = 5
        """
        program_path = test_suite_path / "lists" / "list_construction.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 5, f"Expected 5, got {result}"
    
    def test_cons_associativity(self, saltino_executor, test_suite_path):
        """
        Test cons associativity operations (right-associative)
        Program: Tests that 1::2::3::[] equals 1::(2::(3::[]))
        Both lists should be [1,2,3], accessing all elements twice
        Expected: (1+2+3) + (1+2+3) = 6 + 6 = 12
        """
        program_path = test_suite_path / "lists" / "cons_associativity.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 12, f"Expected 12, got {result}"
    
    def test_dynamic_list_construction(self, saltino_executor, test_suite_path):
        """
        Test dynamic list construction
        Program: build_list(5) creates [5,4,3,2,1] and sums it
        Expected: 5+4+3+2+1 = 15
        """
        program_path = test_suite_path / "lists" / "dynamic_list_construction.salt"
        result, error = saltino_executor(program_path)
        
        assert error is None, f"Program execution failed: {error}"
        assert result == 15, f"Expected 15, got {result}"
