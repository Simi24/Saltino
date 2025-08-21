"""
Conftest file for pytest configuration and shared fixtures
"""
import pytest
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import exec_saltino_iterative

@pytest.fixture
def test_suite_path():
    """Path to the test_suite directory"""
    return project_root / "test_suite"

def execute_saltino_program(program_path):
    """
    Helper function to execute a Saltino program and return the result
    """
    try:
        result = exec_saltino_iterative(str(program_path))
        return result, None
    except Exception as e:
        return None, str(e)

@pytest.fixture
def saltino_executor():
    """Fixture that provides a function to execute Saltino programs"""
    def _execute(program_path):
        return execute_saltino_program(program_path)
    return _execute
