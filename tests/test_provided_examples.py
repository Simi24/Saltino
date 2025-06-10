import os
import pytest
from main import exec_saltino_iterative

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), '../provided_examples')

# Each tuple: (filename, expected_result)
EXAMPLES = [
    ("append.salt", 1),
    ("compose.salt", 4),
    ("dot_product.salt", 11),  # 1*3 + 2*4 = 3 + 8 = 11
    ("fact.salt", 120),
    ("filter.salt", 123),  # head([-99,0,123] filtered by positive is 123
    ("map.salt", 2),
    ("max.salt", 2),
    ("min.salt", 1),
    ("odd.salt", 1),
    ("sign.salt", -1),
    ("square.salt", 4),
    ("sum.salt", 1),
    ("sum2.salt", 3),
]

def run_example(filename):
    path = os.path.join(EXAMPLES_DIR, filename)
    return exec_saltino_iterative(path)

@pytest.mark.parametrize("filename,expected", EXAMPLES)
def test_provided_example(filename, expected):
    result = run_example(filename)
    assert result == expected
