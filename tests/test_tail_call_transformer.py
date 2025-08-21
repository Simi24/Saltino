"""
Test suite for TailCallTransformer module.

Tests the transformation of recursive functions to tail-recursive form,
covering various patterns and edge cases.
"""

import pytest
from AST.ASTNodes import *
from tail_recursive_transformer import TailCallTransformer, analyze_function_pattern


class TestHelpers:
    """Helper methods for creating AST nodes easily in tests."""

    @staticmethod
    def create_simple_factorial() -> Function:
        """Create AST for: factorial(n) = if (n <= 1) then 1 else n * factorial(n - 1)"""
        factorial_body = Block([
            ReturnStatement(
                IfStatement(
                    condition=ComparisonCondition(
                        left=Identifier("n"),
                        operator="<=",
                        right=IntegerLiteral(1)
                    ),
                    then_block=Block([
                        ReturnStatement(IntegerLiteral(1))
                    ]),
                    else_block=Block([
                        ReturnStatement(
                            BinaryExpression(
                                left=Identifier("n"),
                                operator="*",
                                right=FunctionCall(
                                    function=Identifier("factorial"),
                                    arguments=[
                                        BinaryExpression(
                                            left=Identifier("n"),
                                            operator="-",
                                            right=IntegerLiteral(1)
                                        )
                                    ]
                                )
                            )
                        )
                    ])
                )
            )
        ])
        return Function("factorial", ["n"], factorial_body)

    @staticmethod
    def create_simple_sum(n_param: str = "n") -> Function:
        """Create AST for: sum(n) = if (n <= 0) then 0 else n + sum(n - 1)"""
        sum_body = Block([
            ReturnStatement(
                IfStatement(
                    condition=ComparisonCondition(
                        left=Identifier(n_param),
                        operator="<=",
                        right=IntegerLiteral(0)
                    ),
                    then_block=Block([
                        ReturnStatement(IntegerLiteral(0))
                    ]),
                    else_block=Block([
                        ReturnStatement(
                            BinaryExpression(
                                left=Identifier(n_param),
                                operator="+",
                                right=FunctionCall(
                                    function=Identifier("sum"),
                                    arguments=[
                                        BinaryExpression(
                                            left=Identifier(n_param),
                                            operator="-",
                                            right=IntegerLiteral(1)
                                        )
                                    ]
                                )
                            )
                        )
                    ])
                )
            )
        ])
        return Function("sum", [n_param], sum_body)

    @staticmethod
    def create_non_recursive_function() -> Function:
        """Create AST for: simple(x) = x + 1 (not recursive, should not be transformed)"""
        simple_body = Block([
            ReturnStatement(
                BinaryExpression(
                    left=Identifier("x"),
                    operator="+",
                    right=IntegerLiteral(1)
                )
            )
        ])
        return Function("simple", ["x"], simple_body)

    @staticmethod
    def create_multi_param_function() -> Function:
        """Create AST for: add(x, y) = x + y (multiple params, should not be transformed)"""
        add_body = Block([
            ReturnStatement(
                BinaryExpression(
                    left=Identifier("x"),
                    operator="+",
                    right=Identifier("y")
                )
            )
        ])
        return Function("add", ["x", "y"], add_body)

    @staticmethod
    def create_list_length() -> Function:
        """Create AST for: length(lst) = if (lst == []) then 0 else 1 + length(tail(lst))"""
        length_body = Block([
            ReturnStatement(
                IfStatement(
                    condition=ComparisonCondition(
                        left=Identifier("lst"),
                        operator="==",
                        right=EmptyList()
                    ),
                    then_block=Block([
                        ReturnStatement(IntegerLiteral(0))
                    ]),
                    else_block=Block([
                        ReturnStatement(
                            BinaryExpression(
                                left=IntegerLiteral(1),
                                operator="+",
                                right=FunctionCall(
                                    function=Identifier("length"),
                                    arguments=[
                                        FunctionCall(
                                            function=Identifier("tail"),
                                            arguments=[Identifier("lst")]
                                        )
                                    ]
                                )
                            )
                        )
                    ])
                )
            )
        ])
        return Function("length", ["lst"], length_body)

    @staticmethod
    def create_sum_list() -> Function:
        """Create AST for: sum_list(xs) = if (xs == []) then 0 else head(xs) + sum_list(tail(xs))"""
        sum_list_body = Block([
            ReturnStatement(
                IfStatement(
                    condition=ComparisonCondition(
                        left=Identifier("xs"),
                        operator="==",
                        right=EmptyList()
                    ),
                    then_block=Block([
                        ReturnStatement(IntegerLiteral(0))
                    ]),
                    else_block=Block([
                        ReturnStatement(
                            BinaryExpression(
                                left=FunctionCall(
                                    function=Identifier("head"),
                                    arguments=[Identifier("xs")]
                                ),
                                operator="+",
                                right=FunctionCall(
                                    function=Identifier("sum_list"),
                                    arguments=[
                                        FunctionCall(
                                            function=Identifier("tail"),
                                            arguments=[Identifier("xs")]
                                        )
                                    ]
                                )
                            )
                        )
                    ])
                )
            )
        ])
        return Function("sum_list", ["xs"], sum_list_body)

    @staticmethod
    def create_product_list() -> Function:
        """Create AST for: product_list(xs) = if (xs == []) then 1 else head(xs) * product_list(tail(xs))"""
        product_list_body = Block([
            ReturnStatement(
                IfStatement(
                    condition=ComparisonCondition(
                        left=Identifier("xs"),
                        operator="==",
                        right=EmptyList()
                    ),
                    then_block=Block([
                        ReturnStatement(IntegerLiteral(1))
                    ]),
                    else_block=Block([
                        ReturnStatement(
                            BinaryExpression(
                                left=FunctionCall(
                                    function=Identifier("head"),
                                    arguments=[Identifier("xs")]
                                ),
                                operator="*",
                                right=FunctionCall(
                                    function=Identifier("product_list"),
                                    arguments=[
                                        FunctionCall(
                                            function=Identifier("tail"),
                                            arguments=[Identifier("xs")]
                                        )
                                    ]
                                )
                            )
                        )
                    ])
                )
            )
        ])
        return Function("product_list", ["xs"], product_list_body)

    @staticmethod
    def create_dot_product() -> Function:
        """Create AST for: dot_product(xs, ys) = if (xs == []) then 0 else (head(xs) * head(ys)) + dot_product(tail(xs), tail(ys))"""
        dot_product_body = Block([
            ReturnStatement(
                IfStatement(
                    condition=ComparisonCondition(
                        left=Identifier("xs"),
                        operator="==",
                        right=EmptyList()
                    ),
                    then_block=Block([
                        ReturnStatement(IntegerLiteral(0))
                    ]),
                    else_block=Block([
                        ReturnStatement(
                            BinaryExpression(
                                left=BinaryExpression(
                                    left=FunctionCall(
                                        function=Identifier("head"),
                                        arguments=[Identifier("xs")]
                                    ),
                                    operator="*",
                                    right=FunctionCall(
                                        function=Identifier("head"),
                                        arguments=[Identifier("ys")]
                                    )
                                ),
                                operator="+",
                                right=FunctionCall(
                                    function=Identifier("dot_product"),
                                    arguments=[
                                        FunctionCall(
                                            function=Identifier("tail"),
                                            arguments=[Identifier("xs")]
                                        ),
                                        FunctionCall(
                                            function=Identifier("tail"),
                                            arguments=[Identifier("ys")]
                                        )
                                    ]
                                )
                            )
                        )
                    ])
                )
            )
        ])
        return Function("dot_product", ["xs", "ys"], dot_product_body)

    @staticmethod
    def create_reverse_list() -> Function:
        """Create AST for a function that reverses a list using head/tail."""
        # reverse(xs) = if (xs == []) then [] else reverse(tail(xs)) :: [head(xs)]
        return Function(
            name="reverse",
            parameters=["xs"],
            body=Block([
                ReturnStatement(
                    IfStatement(
                        condition=ComparisonCondition(
                            left=Identifier("xs"),
                            operator="==",
                            right=EmptyList()
                        ),
                        then_block=Block([
                            ReturnStatement(EmptyList())
                        ]),
                        else_block=Block([
                            ReturnStatement(
                                BinaryExpression(
                                    left=FunctionCall(
                                        function=Identifier("reverse"),
                                        arguments=[
                                            FunctionCall(
                                                function=Identifier("tail"),
                                                arguments=[Identifier("xs")]
                                            )
                                        ]
                                    ),
                                    operator="::",
                                    right=FunctionCall(
                                        function=Identifier("head"),
                                        arguments=[Identifier("xs")]
                                    )
                                )
                            )
                        ])
                    )
                )
            ])
        )

    @staticmethod
    def create_flexible_param_function() -> Function:
        """Create AST for a function that uses parameters in flexible order."""
        # flex_func(x, y) = if (x == 0) then 0 else flex_func(y, x-1)
        return Function(
            name="flex_func",
            parameters=["x", "y"],
            body=Block([
                ReturnStatement(
                    IfStatement(
                        condition=ComparisonCondition(
                            left=Identifier("x"),
                            operator="==",
                            right=IntegerLiteral(0)
                        ),
                        then_block=Block([
                            ReturnStatement(IntegerLiteral(0))
                        ]),
                        else_block=Block([
                            ReturnStatement(
                                FunctionCall(
                                    function=Identifier("flex_func"),
                                    arguments=[
                                        Identifier("y"),
                                        BinaryExpression(
                                            left=Identifier("x"),
                                            operator="-",
                                            right=IntegerLiteral(1)
                                        )
                                    ]
                                )
                            )
                        ])
                    )
                )
            ])
        )


class TestTailCallTransformer:
    """Test cases for the TailCallTransformer class."""

    def setup_method(self):
        """Set up fresh transformer for each test."""
        self.transformer = TailCallTransformer()

    def test_initialization(self):
        """Test that transformer initializes correctly."""
        assert self.transformer.helper_functions == []
        assert self.transformer.name_counters == {}

    def test_unique_name_generation(self):
        """Test unique name generation functionality."""
        # First call should generate name_1
        name1 = self.transformer._get_unique_name("factorial_helper")
        assert name1 == "factorial_helper_1"

        # Second call should generate name_2
        name2 = self.transformer._get_unique_name("factorial_helper")
        assert name2 == "factorial_helper_2"

        # Different base name should start at 1
        name3 = self.transformer._get_unique_name("acc")
        assert name3 == "acc_1"

    def test_factorial_pattern_recognition(self):
        """Test that factorial pattern is correctly recognized."""
        factorial_func = TestHelpers.create_simple_factorial()
        pattern_info = self.transformer._match_pattern(factorial_func)

        assert pattern_info is not None, "Factorial pattern should be recognized"
        assert pattern_info['main_param'] == "n"
        assert pattern_info['operator'] == "*"
        assert isinstance(pattern_info['base_value'], IntegerLiteral)
        assert pattern_info['base_value'].value == 1
        assert isinstance(
            pattern_info['initial_accumulator_value'], IntegerLiteral)
        assert pattern_info['initial_accumulator_value'].value == 1

    def test_sum_pattern_recognition(self):
        """Test that sum pattern is correctly recognized."""
        sum_func = TestHelpers.create_simple_sum()
        pattern_info = self.transformer._match_pattern(sum_func)

        assert pattern_info is not None, "Sum pattern should be recognized"
        assert pattern_info['main_param'] == "n"
        assert pattern_info['operator'] == "+"
        assert isinstance(pattern_info['base_value'], IntegerLiteral)
        assert pattern_info['base_value'].value == 0
        assert isinstance(
            pattern_info['initial_accumulator_value'], IntegerLiteral)
        assert pattern_info['initial_accumulator_value'].value == 0

    def test_non_recursive_rejection(self):
        """Test that non-recursive functions are correctly rejected."""
        non_recursive = TestHelpers.create_non_recursive_function()
        pattern_info = self.transformer._match_pattern(non_recursive)

        assert pattern_info is None, "Non-recursive function should be rejected"

    def test_multi_param_rejection(self):
        """Test that multi-parameter functions are correctly rejected."""
        multi_param = TestHelpers.create_multi_param_function()
        pattern_info = self.transformer._match_pattern(multi_param)

        assert pattern_info is None, "Multi-parameter function should be rejected"

    def test_factorial_transformation(self):
        """Test complete transformation of factorial function."""
        factorial_func = TestHelpers.create_simple_factorial()
        program = Program([factorial_func])

        transformed_program = self.transformer.transform_program(program)

        # Should have original factorial (now wrapper) + helper function
        assert len(
            transformed_program.functions) == 2, f"Expected 2 functions, got {len(transformed_program.functions)}"

        # Find the functions
        wrapper_func = None
        helper_func = None

        for func in transformed_program.functions:
            if func.name == "factorial":
                wrapper_func = func
            elif "factorial_tc_helper" in func.name:
                helper_func = func

        assert wrapper_func is not None, "Wrapper function should exist"
        assert helper_func is not None, "Helper function should exist"

        # Check wrapper function
        assert wrapper_func.parameters == [
            "n"], "Wrapper should maintain original parameters"
        assert len(
            wrapper_func.body.statements) == 1, "Wrapper should have single return statement"
        assert isinstance(
            wrapper_func.body.statements[0], ReturnStatement), "Wrapper should return helper call"

        # Check helper function
        assert len(
            helper_func.parameters) == 2, "Helper should have 2 parameters (n + accumulator)"
        assert helper_func.parameters[0] == "n", "First parameter should be original parameter"
        assert "acc" in helper_func.parameters[1], "Second parameter should be accumulator"

    def test_sum_transformation(self):
        """Test complete transformation of sum function."""
        sum_func = TestHelpers.create_simple_sum()
        program = Program([sum_func])

        transformed_program = self.transformer.transform_program(program)

        # Should have original sum (now wrapper) + helper function
        assert len(
            transformed_program.functions) == 2, f"Expected 2 functions, got {len(transformed_program.functions)}"

        # Find the functions
        wrapper_func = None
        helper_func = None

        for func in transformed_program.functions:
            if func.name == "sum":
                wrapper_func = func
            elif "sum_tc_helper" in func.name:
                helper_func = func

        assert wrapper_func is not None, "Wrapper function should exist"
        assert helper_func is not None, "Helper function should exist"

        # Verify transformation maintains function structure
        assert wrapper_func.parameters == [
            "n"], "Wrapper should maintain original parameters"
        assert len(helper_func.parameters) == 2, "Helper should have 2 parameters"

    def test_no_transformation_preserves_original(self):
        """Test that functions that can't be transformed are preserved unchanged."""
        non_recursive = TestHelpers.create_non_recursive_function()
        program = Program([non_recursive])

        transformed_program = self.transformer.transform_program(program)

        # Should have only the original function, unchanged
        assert len(
            transformed_program.functions) == 1, "Should have exactly one function"
        assert transformed_program.functions[0].name == "simple", "Should preserve original function"
        assert transformed_program.functions[0].parameters == [
            "x"], "Should preserve original parameters"

    def test_multiple_functions_mixed(self):
        """Test transformation of program with both transformable and non-transformable functions."""
        factorial = TestHelpers.create_simple_factorial()
        non_recursive = TestHelpers.create_non_recursive_function()
        program = Program([factorial, non_recursive])

        transformed_program = self.transformer.transform_program(program)

        # Should have: factorial wrapper + factorial helper + simple (unchanged)
        assert len(
            transformed_program.functions) == 3, f"Expected 3 functions, got {len(transformed_program.functions)}"

        # Check that we have the expected functions
        function_names = [f.name for f in transformed_program.functions]
        assert "factorial" in function_names, "Should have factorial wrapper"
        assert "simple" in function_names, "Should have unchanged simple function"

        # Should have one helper function
        helper_functions = [
            f for f in transformed_program.functions if "tc_helper" in f.name]
        assert len(
            helper_functions) == 1, "Should have exactly one helper function"

    def test_list_length_pattern_recognition(self):
        """Test that list length pattern is correctly recognized."""
        length_func = TestHelpers.create_list_length()
        pattern_info = self.transformer._match_pattern(length_func)

        assert pattern_info is not None, "List length pattern should be recognized"
        assert pattern_info['main_param'] == "lst"
        assert pattern_info['operator'] == "+"
        assert isinstance(pattern_info['base_value'], EmptyList)
        assert isinstance(
            pattern_info['initial_accumulator_value'], IntegerLiteral)
        assert pattern_info['initial_accumulator_value'].value == 0

    def test_list_length_transformation(self):
        """Test complete transformation of list length function."""
        length_func = TestHelpers.create_list_length()
        program = Program([length_func])

        transformed_program = self.transformer.transform_program(program)

        # Should have original length (now wrapper) + helper function
        assert len(
            transformed_program.functions) == 2, f"Expected 2 functions, got {len(transformed_program.functions)}"

        # Find the functions
        wrapper_func = None
        helper_func = None

        for func in transformed_program.functions:
            if func.name == "length":
                wrapper_func = func
            elif "length_tc_helper" in func.name:
                helper_func = func

        assert wrapper_func is not None, "Wrapper function should exist"
        assert helper_func is not None, "Helper function should exist"

        # Check wrapper function
        assert wrapper_func.parameters == [
            "lst"], "Wrapper should maintain original parameters"
        assert len(
            wrapper_func.body.statements) == 1, "Wrapper should have single return statement"
        assert isinstance(
            wrapper_func.body.statements[0], ReturnStatement), "Wrapper should return helper call"

        # Check helper function
        assert len(
            helper_func.parameters) == 2, "Helper should have 2 parameters (lst + accumulator)"
        assert helper_func.parameters[0] == "lst", "First parameter should be original parameter"
        assert "acc" in helper_func.parameters[1], "Second parameter should be accumulator"

    def test_sum_list_pattern_recognition(self):
        """Test that sum_list pattern with head(xs) is correctly recognized."""
        sum_list_func = TestHelpers.create_sum_list()
        pattern_info = self.transformer._match_pattern(sum_list_func)

        assert pattern_info is not None, "Sum list pattern should be recognized"
        assert pattern_info['main_param'] == "xs"
        assert pattern_info['operator'] == "+"
        assert isinstance(pattern_info['base_value'], EmptyList)
        assert isinstance(
            pattern_info['initial_accumulator_value'], IntegerLiteral)
        assert pattern_info['initial_accumulator_value'].value == 0
        # The other operand should be head(xs) function call
        assert isinstance(pattern_info['other_operand'], FunctionCall)
        assert pattern_info['other_operand'].function.name == "head"

    def test_product_list_pattern_recognition(self):
        """Test that product_list pattern with head(xs) is correctly recognized."""
        product_list_func = TestHelpers.create_product_list()
        pattern_info = self.transformer._match_pattern(product_list_func)

        assert pattern_info is not None, "Product list pattern should be recognized"
        assert pattern_info['main_param'] == "xs"
        assert pattern_info['operator'] == "*"
        assert isinstance(pattern_info['base_value'], EmptyList)
        assert isinstance(
            pattern_info['initial_accumulator_value'], IntegerLiteral)
        assert pattern_info['initial_accumulator_value'].value == 1
        # The other operand should be head(xs) function call
        assert isinstance(pattern_info['other_operand'], FunctionCall)
        assert pattern_info['other_operand'].function.name == "head"

    def test_sum_list_transformation(self):
        """Test complete transformation of sum_list function."""
        sum_list_func = TestHelpers.create_sum_list()
        program = Program([sum_list_func])

        transformed_program = self.transformer.transform_program(program)

        # Should have original sum_list (now wrapper) + helper function
        assert len(
            transformed_program.functions) == 2, f"Expected 2 functions, got {len(transformed_program.functions)}"

        # Find the functions
        wrapper_func = None
        helper_func = None

        for func in transformed_program.functions:
            if func.name == "sum_list":
                wrapper_func = func
            elif "sum_list_tc_helper" in func.name:
                helper_func = func

        assert wrapper_func is not None, "Wrapper function should exist"
        assert helper_func is not None, "Helper function should exist"

        # Check wrapper function
        assert wrapper_func.parameters == [
            "xs"], "Wrapper should maintain original parameters"
        assert len(
            wrapper_func.body.statements) == 1, "Wrapper should have single return statement"

        # Check helper function
        assert len(
            helper_func.parameters) == 2, "Helper should have 2 parameters (xs + accumulator)"
        assert helper_func.parameters[0] == "xs", "First parameter should be original parameter"
        assert "acc" in helper_func.parameters[1], "Second parameter should be accumulator"

    def test_product_list_transformation(self):
        """Test complete transformation of product_list function."""
        product_list_func = TestHelpers.create_product_list()
        program = Program([product_list_func])

        transformed_program = self.transformer.transform_program(program)

        # Should have original product_list (now wrapper) + helper function
        assert len(
            transformed_program.functions) == 2, f"Expected 2 functions, got {len(transformed_program.functions)}"

        # Find the functions
        wrapper_func = None
        helper_func = None

        for func in transformed_program.functions:
            if func.name == "product_list":
                wrapper_func = func
            elif "product_list_tc_helper" in func.name:
                helper_func = func

        assert wrapper_func is not None, "Wrapper function should exist"
        assert helper_func is not None, "Helper function should exist"

        # Check wrapper function
        assert wrapper_func.parameters == [
            "xs"], "Wrapper should maintain original parameters"

        # Check helper function
        assert len(
            helper_func.parameters) == 2, "Helper should have 2 parameters (xs + accumulator)"
        assert helper_func.parameters[0] == "xs", "First parameter should be original parameter"
        assert "acc" in helper_func.parameters[1], "Second parameter should be accumulator"

    def test_analyze_factorial(self):
        """Test analysis of factorial function."""
        factorial = TestHelpers.create_simple_factorial()
        analysis = analyze_function_pattern(factorial)

        assert analysis['function_name'] == "factorial"
        assert analysis['can_transform'] == True
        assert 'pattern_info' in analysis
        assert analysis['pattern_info']['main_parameter'] == "n"
        assert analysis['pattern_info']['operator'] == "*"

    def test_analyze_non_recursive(self):
        """Test analysis of non-recursive function."""
        simple = TestHelpers.create_non_recursive_function()
        analysis = analyze_function_pattern(simple)

        assert analysis['function_name'] == "simple"
        assert analysis['can_transform'] == False
        assert 'reason' in analysis
        assert analysis['reason'] is not None

    def test_analyze_multi_param(self):
        """Test analysis of multi-parameter function."""
        multi_param = TestHelpers.create_multi_param_function()
        analysis = analyze_function_pattern(multi_param)

        assert analysis['function_name'] == "add"
        assert analysis['can_transform'] == False
        assert 'reason' in analysis
        # The add function has 2 parameters but doesn't match recursive pattern
        assert "structure" in analysis['reason']

    def test_analyze_length(self):
        """Test analysis of list length function."""
        length_func = TestHelpers.create_list_length()
        analysis = analyze_function_pattern(length_func)

        assert analysis['function_name'] == "length"
        assert analysis['can_transform'] == True
        assert 'pattern_info' in analysis
        assert analysis['pattern_info']['main_parameter'] == "lst"
        assert analysis['pattern_info']['operator'] == "+"

    def test_analyze_sum_list(self):
        """Test analysis of sum_list function."""
        sum_list_func = TestHelpers.create_sum_list()
        analysis = analyze_function_pattern(sum_list_func)

        assert analysis['function_name'] == "sum_list"
        assert analysis['can_transform'] == True
        assert 'pattern_info' in analysis
        assert analysis['pattern_info']['main_parameter'] == "xs"
        assert analysis['pattern_info']['operator'] == "+"

    def test_analyze_product_list(self):
        """Test analysis of product_list function."""
        product_list_func = TestHelpers.create_product_list()
        analysis = analyze_function_pattern(product_list_func)

        assert analysis['function_name'] == "product_list"
        assert analysis['can_transform'] == True
        assert 'pattern_info' in analysis
        assert analysis['pattern_info']['main_parameter'] == "xs"
        assert analysis['pattern_info']['operator'] == "*"

    def test_analyze_dot_product_now_works(self):
        """Test that dot_product analysis now works with 2-parameter support."""
        dot_product_func = TestHelpers.create_dot_product()
        analysis = analyze_function_pattern(dot_product_func)

        assert analysis['function_name'] == "dot_product"
        assert analysis['can_transform'] == True
        assert 'pattern_info' in analysis
        assert analysis['pattern_info']['main_parameter'] == "xs"
        assert analysis['pattern_info']['operator'] == "+"

    def test_dot_product_transformation(self):
        """Test complete transformation of dot_product function."""
        dot_product_func = TestHelpers.create_dot_product()
        program = Program([dot_product_func])

        transformed_program = self.transformer.transform_program(program)

        # Should have original dot_product (now wrapper) + helper function
        assert len(
            transformed_program.functions) == 2, f"Expected 2 functions, got {len(transformed_program.functions)}"

        # Find the functions
        wrapper_func = None
        helper_func = None

        for func in transformed_program.functions:
            if func.name == "dot_product":
                wrapper_func = func
            elif "dot_product_tc_helper" in func.name:
                helper_func = func

        assert wrapper_func is not None, "Wrapper function should exist"
        assert helper_func is not None, "Helper function should exist"

        # Check wrapper function
        assert wrapper_func.parameters == [
            "xs", "ys"], "Wrapper should maintain original parameters"
        assert len(
            wrapper_func.body.statements) == 1, "Wrapper should have single return statement"

        # Check helper function
        assert len(
            helper_func.parameters) == 3, "Helper should have 3 parameters (xs, ys + accumulator)"
        assert helper_func.parameters[0] == "xs", "First parameter should be first original parameter"
        assert helper_func.parameters[1] == "ys", "Second parameter should be second original parameter"
        assert "acc" in helper_func.parameters[2], "Third parameter should be accumulator"

    def test_reverse_list_transformation(self):
        """Test that list reversal function with :: is not transformed."""
        reverse_func = TestHelpers.create_reverse_list()
        program = Program([reverse_func])

        transformed_program = self.transformer.transform_program(program)

        # Function with :: operator should not be transformed
        assert len(transformed_program.functions) == 1, "Function with :: operator should not be transformed"
        assert transformed_program.functions[0].name == "reverse", "Original function should be preserved unchanged"
        assert transformed_program.functions[0] == reverse_func, "Function should be completely unchanged"

    def test_flex_func_transformation(self):
        """Test complete transformation of flex_func function."""
        flex_func = TestHelpers.create_flexible_param_function()
        program = Program([flex_func])

        transformed_program = self.transformer.transform_program(program)

        # Should have original flex_func (now wrapper) + helper function
        assert len(transformed_program.functions) == 2, f"Expected 2 functions, got {len(transformed_program.functions)}"

        # Find wrapper and helper functions
        wrapper_func = None
        helper_func = None

        for func in transformed_program.functions:
            if func.name == "flex_func":
                wrapper_func = func
            elif "tc_helper" in func.name:
                helper_func = func

        assert wrapper_func is not None, "Should have wrapper function"
        assert helper_func is not None, "Should have helper function"

        # Check parameters
        assert wrapper_func.parameters == ["x", "y"], "Wrapper should maintain two parameters"
        assert len(helper_func.parameters) == 3, "Helper should have three parameters (x, y, acc)"


if __name__ == "__main__":
    # Run basic tests manually if called directly
    print("Running basic tests...")

    helpers = TestHelpers()

    # Test AST creation
    factorial = helpers.create_simple_factorial()
    print(
        f"✓ Created factorial function: {factorial.name}({factorial.parameters})")

    sum_func = helpers.create_simple_sum()
    print(f"✓ Created sum function: {sum_func.name}({sum_func.parameters})")

    # Test transformer
    transformer = TailCallTransformer()
    print(f"✓ Created transformer")

    # Test pattern recognition
    pattern = transformer._match_pattern(factorial)
    if pattern:
        print(
            f"✓ Factorial pattern recognized: {pattern['operator']} operation")
    else:
        print("✗ Factorial pattern not recognized")

    # Test transformation
    program = Program([factorial])
    transformed = transformer.transform_program(program)
    print(
        f"✓ Transformation completed: {len(program.functions)} -> {len(transformed.functions)} functions")

    print("\nBasic tests completed! Run with pytest for full test suite.")
