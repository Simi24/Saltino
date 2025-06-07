# Saltino Test Suite

This directory contains the test suite for the Saltino programming language interpreter. The tests are organized by functionality and use pytest as the testing framework.

## Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

## Test Organization

The tests are organized into the following modules:

- `test_arithmetic.py` - Tests for arithmetic operations
- `test_basic_functionality.py` - Tests for basic language functionality
- `test_conditions.py` - Tests for conditional statements
- `test_error_cases.py` - Tests for error handling
- `test_functions.py` - Tests for function definitions and calls
- `test_lists.py` - Tests for list operations

## Running Tests

### Run All Tests

To run the entire test suite:

```bash
pytest
```

### Run Tests by Category

Tests are marked with categories. You can run specific categories using the `-m` flag:

```bash
# Run arithmetic tests
pytest -m arithmetic

# Run condition tests
pytest -m conditions

# Run function tests
pytest -m functions

# Run list operation tests
pytest -m lists

# Run basic functionality tests
pytest -m basic

# Run error handling tests
pytest -m error_cases

# Run edge case tests
pytest -m edge_cases
```

### Run Specific Test Files

To run tests from a specific file:

```bash
# Run only arithmetic tests
pytest tests/test_arithmetic.py

# Run only condition tests
pytest tests/test_conditions.py

# Run only function tests
pytest tests/test_functions.py
```

### Run Specific Test Methods

To run a specific test method:

```bash
pytest tests/test_conditions.py::TestConditions::test_boolean_literal
```

### Run Tests with Verbose Output

For more detailed output:

```bash
pytest -v
```

### Run Tests with HTML Report

The test suite is configured to generate an HTML report automatically:

```bash
pytest
```

The report will be generated at `reports/report.html` and can be opened in a web browser.

## Test Configuration

The test configuration is defined in `pytest.ini`:

- **Test Discovery**: Automatically finds files matching `test_*.py` pattern
- **Markers**: Custom markers for categorizing tests
- **HTML Reports**: Generates self-contained HTML reports
- **Output Format**: Short traceback format for cleaner error messages

## Available Test Markers

- `arithmetic` - Arithmetic operations
- `basic` - Basic functionality
- `conditions` - Conditional statements
- `functions` - Function definitions and calls
- `lists` - List operations
- `variables` - Variable scope
- `edge_cases` - Edge cases
- `error_cases` - Error handling

## Test Structure

Each test class follows a consistent pattern:

1. **Class-based organization** - Tests are grouped in classes by functionality
2. **Descriptive docstrings** - Each test includes program logic and expected results
3. **Fixtures** - Uses `saltino_executor` fixture for running Saltino programs
4. **Assertions** - Clear error messages for failed assertions

## Example Usage

```bash
# Run all tests with verbose output
pytest -v

# Run only condition tests
pytest -m conditions

# Run tests and generate HTML report (default behavior)
pytest

# Run a specific test file with detailed output
pytest tests/test_arithmetic.py -v
```

## Troubleshooting

If tests fail:

1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Ensure the Saltino grammar is properly generated in the `Grammatica/` directory
3. Verify that test programs exist in the `test_suite/` directory
4. Check the HTML report at `reports/report.html` for detailed error information

## Contributing

When adding new tests:

1. Follow the existing naming convention (`test_*.py`)
2. Use appropriate markers to categorize tests
3. Include descriptive docstrings explaining the test logic
4. Follow the existing test structure and patterns
