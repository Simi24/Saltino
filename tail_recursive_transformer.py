"""
Tail Call Transformer for converting non-tail-recursive functions to tail-recursive form.

This module analyzes the Abstract Syntax Tree (AST) of a program and looks for specific,
predefined patterns of non-tail-recursive functions. When such patterns are found,
it rewrites that part of the AST, converting the targeted function into a structure
that uses tail recursion by creating a "helper" function with an accumulator and
a "wrapper" function that maintains the original function's signature.
"""

from AST.ASTNodes import *
from typing import Dict, List, Optional, Any
import copy


class TailCallTransformer:
    """
    Transformer that converts non-tail-recursive functions to tail-recursive form.

    Analyzes AST patterns and creates helper functions with accumulators to enable
    tail call optimization for functions matching specific recursive patterns.
    """

    def __init__(self):
        """Initialize the transformer with fresh state for each transformation pass."""
        # List to store new helper functions generated during transformation
        self.helper_functions: List[Function] = []

        # Counters for generating unique names (reset per program)
        self.name_counters: Dict[str, int] = {}

    def _get_unique_name(self, base_name: str) -> str:
        """
        Generate a unique name by appending a counter to the base name.

        Args:
            base_name: The base name to make unique (e.g., "factorial_helper", "acc")

        Returns:
            A unique string combining base_name and counter (e.g., "factorial_helper_1")
        """
        if base_name not in self.name_counters:
            self.name_counters[base_name] = 0

        self.name_counters[base_name] += 1
        return f"{base_name}_{self.name_counters[base_name]}"

    def transform_program(self, program: Program) -> Program:
        """
        Transform an entire program by analyzing each function for tail call optimization.

        Args:
            program: The root AST node representing the entire program

        Returns:
            A new Program AST node with transformed functions and generated helpers
        """
        # Reset state for fresh transformation pass
        self.helper_functions = []
        self.name_counters = {}

        # Store original/wrapper functions
        transformed_functions = []

        # Process each function in the program
        for function in program.functions:
            # Attempt transformation on this function
            result_function = self._try_transform_recursive_pattern(function)
            transformed_functions.append(result_function)

        # Assemble new program with original/wrapper functions + helpers
        all_functions = transformed_functions + self.helper_functions

        return Program(all_functions, program.position)

    def _try_transform_recursive_pattern(self, function: Function) -> Function:
        """
        Analyze a single function to see if it matches a transformable pattern.

        Args:
            function: AST node representing a single function definition

        Returns:
            Either the original function AST (if no transformation) or a new wrapper function AST
        """
        # A. Pattern Matching Phase
        pattern_info = self._match_pattern(function)

        if pattern_info is None:
            # Pattern didn't match, return original function
            return function

        # B. AST Rewriting Phase
        return self._rewrite_function(function, pattern_info)

    def _match_pattern(self, function: Function) -> Optional[Dict[str, Any]]:
        """Check if function matches any of the supported recursive patterns."""

        # 1. Parameter Check: exactly one or two main parameters
        if len(function.parameters) not in [1, 2]:
            return None

        main_param = function.parameters[0]
        second_param = function.parameters[1] if len(
            function.parameters) == 2 else None

        # 2. Body Structure: must be primarily a conditional statement
        if len(function.body.statements) != 1:
            return None

        stmt = function.body.statements[0]

        # Extract the if-statement (could be direct or inside a return)
        if_stmt = None
        if isinstance(stmt, IfStatement):
            if_stmt = stmt
        elif isinstance(stmt, ReturnStatement) and isinstance(stmt.value, IfStatement):
            if_stmt = stmt.value
        else:
            return None

        # 3. Base Case - Condition: comparison involving main parameter and constant
        condition = if_stmt.condition
        base_value = self._extract_base_value(condition, main_param)
        if base_value is None:
            return None

        # 4. Base Case - Return Value: single return with constant literal
        if (len(if_stmt.then_block.statements) != 1 or
                not isinstance(if_stmt.then_block.statements[0], ReturnStatement)):
            return None

        base_return = if_stmt.then_block.statements[0]
        if not isinstance(base_return.value, (IntegerLiteral, BooleanLiteral, Identifier)):
            return None

        initial_accumulator_value = base_return.value

        # 5. Recursive Case - Return Structure: must be either:
        # - A binary operation (e.g., n * factorial(n-1))
        # - A direct recursive call (e.g., flex_func(y, x-1))
        if (if_stmt.else_block is None or
            len(if_stmt.else_block.statements) != 1 or
                not isinstance(if_stmt.else_block.statements[0], ReturnStatement)):
            return None

        recursive_return = if_stmt.else_block.statements[0]
        recursive_value = recursive_return.value

        is_recursive_call_on_left = None
        recursive_call = None
        other_operand = None
        operator = None

        if isinstance(recursive_value, BinaryExpression):
            # Case 1: Binary expression (e.g., n * factorial(n-1))
            binary_expr = recursive_value
            operator = binary_expr.operator

            if operator == "::":
                return None

            if self._is_recursive_call(binary_expr.left, function.name):
                recursive_call = binary_expr.left
                other_operand = binary_expr.right
                is_recursive_call_on_left = True
            elif self._is_recursive_call(binary_expr.right, function.name):
                recursive_call = binary_expr.right
                other_operand = binary_expr.left
                is_recursive_call_on_left = False
            else:
                return None

            # Validate other operand
            if not isinstance(other_operand, (Identifier, IntegerLiteral, BooleanLiteral, FunctionCall, UnaryExpression, BinaryExpression)):
                return None

            if self._is_recursive_call(other_operand, function.name):
                return None

            # Check for non-commutative operators that would require complex transformation
            # subtraction, division, cons, exponentiation
            non_commutative_ops = ["-", "/", "::", "^"]
            if operator in non_commutative_ops and not is_recursive_call_on_left:
                return None

        elif isinstance(recursive_value, FunctionCall) and self._is_recursive_call(recursive_value, function.name):
            # Case 2: Direct recursive call (e.g., flex_func(y, x-1))
            recursive_call = recursive_value
            other_operand = None
            operator = None
            is_recursive_call_on_left = True  # Doesn't matter for direct calls
        else:
            return None

        # Validate recursive call arguments
        if not isinstance(recursive_call, FunctionCall):
            return None

        recursive_args = recursive_call.arguments
        if not self._validate_recursive_args(recursive_args, main_param, second_param):
            return None

        return {
            'main_param': main_param,
            'second_param': second_param,
            'base_value': base_value,
            'initial_accumulator_value': initial_accumulator_value,
            'operator': operator,
            'other_operand': other_operand,
            'recursive_args': recursive_args,
            'condition': condition,
            'is_recursive_call_on_left': is_recursive_call_on_left
        }

    def _extract_base_value(self, condition, main_param: str):
        """Extract the base case value from the condition."""
        if not isinstance(condition, ComparisonCondition):
            return None

        # Check if condition involves the main parameter
        if (isinstance(condition.left, Identifier) and condition.left.name == main_param and
                isinstance(condition.right, (IntegerLiteral, BooleanLiteral, EmptyList))):
            return condition.right
        elif (isinstance(condition.right, Identifier) and condition.right.name == main_param and
              isinstance(condition.left, (IntegerLiteral, BooleanLiteral, EmptyList))):
            return condition.left

        return None

    def _is_recursive_call(self, expr, function_name: str) -> bool:
        """Check if expression is a direct recursive call to the current function."""
        return (isinstance(expr, FunctionCall) and
                isinstance(expr.function, Identifier) and
                expr.function.name == function_name)

    def _validate_recursive_args(self, args: List, main_param: str, second_param: str = None) -> bool:
        """Validate that recursive call arguments follow expected pattern."""
        # For single parameter functions
        if second_param is None:
            if len(args) != 1:
                return False

            arg = args[0]

            # Should be a modification of main parameter (e.g., param - 1, param + 1)
            # OR a function call operating on the main parameter (e.g., tail(lst))
            # OR a unary expression operating on the main parameter (e.g., tail lst)
            if isinstance(arg, BinaryExpression):
                if (isinstance(arg.left, Identifier) and arg.left.name == main_param and
                        isinstance(arg.right, (IntegerLiteral, BooleanLiteral))):
                    return True
                elif (isinstance(arg.right, Identifier) and arg.right.name == main_param and
                      isinstance(arg.left, (IntegerLiteral, BooleanLiteral))):
                    return True
            elif isinstance(arg, FunctionCall):
                # Check if it's a function call with the main parameter as argument
                if (len(arg.arguments) == 1 and
                    isinstance(arg.arguments[0], Identifier) and
                        arg.arguments[0].name == main_param):
                    return True
            elif isinstance(arg, UnaryExpression):
                # Check if it's a unary expression with the main parameter as operand
                if (isinstance(arg.operand, Identifier) and
                        arg.operand.name == main_param):
                    return True
            return False

        # For two parameter functions
        else:
            if len(args) != 2:
                return False

            def validates_param_usage(arg, param_name):
                # Direct parameter usage (e.g., ys in append(tail(xs), ys))
                if isinstance(arg, Identifier) and arg.name == param_name:
                    return True
                # Parameter modification (e.g., tail(xs), n-1, etc.)
                if isinstance(arg, BinaryExpression):
                    return ((isinstance(arg.left, Identifier) and arg.left.name == param_name and
                            isinstance(arg.right, (IntegerLiteral, BooleanLiteral))) or
                            (isinstance(arg.right, Identifier) and arg.right.name == param_name and
                            isinstance(arg.left, (IntegerLiteral, BooleanLiteral))))
                elif isinstance(arg, FunctionCall):
                    return (len(arg.arguments) == 1 and
                            isinstance(arg.arguments[0], Identifier) and
                            arg.arguments[0].name == param_name)
                elif isinstance(arg, UnaryExpression):
                    return (isinstance(arg.operand, Identifier) and
                            arg.operand.name == param_name)
                return False

            # Check that each argument corresponds to a valid usage of either parameter
            # but allow them in any order
            arg1_valid = validates_param_usage(
                args[0], main_param) or validates_param_usage(args[0], second_param)
            arg2_valid = validates_param_usage(
                args[1], main_param) or validates_param_usage(args[1], second_param)

            # Make sure both parameters are used exactly once
            uses_main_param = (validates_param_usage(args[0], main_param) or
                               validates_param_usage(args[1], main_param))
            uses_second_param = (validates_param_usage(args[0], second_param) or
                                 validates_param_usage(args[1], second_param))

            return arg1_valid and arg2_valid and uses_main_param and uses_second_param

    def _rewrite_function(self, original_function: Function, pattern_info: Dict[str, Any]) -> Function:
        """
        Rewrite the function using the extracted pattern information.

        Creates a helper function and returns a wrapper function.
        """
        # Generate unique names
        helper_name = self._get_unique_name(
            f"{original_function.name}_tc_helper")
        acc_name = self._get_unique_name("acc")

        # Create helper function
        helper_function = self._create_helper_function(
            original_function, pattern_info, helper_name, acc_name)

        # Store helper function
        self.helper_functions.append(helper_function)

        # Create and return wrapper function
        return self._create_wrapper_function(
            original_function, pattern_info, helper_name, acc_name)

    def _create_helper_function(self, original: Function, pattern_info: Dict[str, Any],
                                helper_name: str, acc_name: str) -> Function:
        """Create the tail-recursive helper function with accumulator."""
        main_param = pattern_info['main_param']
        second_param = pattern_info['second_param']

        # Helper parameters: original parameters + accumulator
        if second_param is None:
            helper_params = [main_param, acc_name]
        else:
            helper_params = [main_param, second_param, acc_name]

        # Base case condition (same as original)
        base_condition = copy.deepcopy(pattern_info['condition'])

        # Base case action: return accumulator
        base_return = ReturnStatement(Identifier(acc_name))
        base_block = Block([base_return])

        # Recursive step: depends on whether we have a binary operation or direct call
        operator = pattern_info['operator']
        if operator is not None:
            # Binary operation case (e.g., n * factorial(n-1))
            # Compute new accumulator value
            new_acc_left = copy.deepcopy(pattern_info['other_operand'])
            new_acc_right = Identifier(acc_name)

            if pattern_info['is_recursive_call_on_left']:
                # Original: recursive_call OP other_operand
                # New: other_operand OP acc
                left_operand = new_acc_left
                right_operand = new_acc_right
            else:
                # Original: other_operand OP recursive_call
                # For non-commutative ops like subtraction, we need: other_operand OP acc
                left_operand = new_acc_left
                right_operand = new_acc_right

            new_acc_expr = BinaryExpression(
                left=left_operand,
                # Explicitly use pattern_info['operator'] as per user's fix
                operator=pattern_info['operator'],
                right=right_operand
            )
        else:
            # Direct recursive call case (e.g., flex_func(y, x-1))
            # Just pass through the accumulator unchanged
            new_acc_expr = Identifier(acc_name)

        # Arguments for tail call
        if second_param is None:
            tail_call_args = [
                # modified main param
                copy.deepcopy(pattern_info['recursive_args'][0]),
                new_acc_expr  # new accumulator value
            ]
        else:
            tail_call_args = [
                # modified main param
                copy.deepcopy(pattern_info['recursive_args'][0]),
                # modified second param
                copy.deepcopy(pattern_info['recursive_args'][1]),
                new_acc_expr  # new accumulator value
            ]

        tail_call = FunctionCall(
            function=Identifier(helper_name),
            arguments=tail_call_args
        )

        recursive_return = ReturnStatement(tail_call)
        recursive_block = Block([recursive_return])

        # Complete if-statement for helper
        helper_if = IfStatement(
            condition=base_condition,
            then_block=base_block,
            else_block=recursive_block
        )

        helper_body = Block([helper_if])

        return Function(
            name=helper_name,
            parameters=helper_params,
            body=helper_body,
            position=original.position
        )

    def _create_wrapper_function(self, original: Function, pattern_info: Dict[str, Any],
                                 helper_name: str, acc_name: str) -> Function:
        """Create the wrapper function that maintains original signature."""
        # Call helper with original parameters + initial accumulator value
        main_param = pattern_info['main_param']
        second_param = pattern_info['second_param']

        if second_param is None:
            wrapper_args = [
                # pass through original param
                Identifier(main_param),
                # initial acc value
                copy.deepcopy(pattern_info['initial_accumulator_value'])
            ]
        else:
            wrapper_args = [
                # pass through original params
                Identifier(main_param),
                Identifier(second_param),
                # initial acc value
                copy.deepcopy(pattern_info['initial_accumulator_value'])
            ]

        wrapper_call = FunctionCall(
            function=Identifier(helper_name),
            arguments=wrapper_args
        )

        wrapper_return = ReturnStatement(wrapper_call)
        wrapper_body = Block([wrapper_return])

        return Function(
            name=original.name,  # Same name as original
            parameters=original.parameters,  # Same parameters as original
            body=wrapper_body,
            position=original.position
        )


def demo_transformation():
    """Demonstrate the use of the TailCallTransformer with a factorial example."""
    # Create an example AST for factorial function
    # factorial(n) = if (n <= 1) then 1 else n * factorial(n - 1)

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

    factorial_func = Function("factorial", ["n"], factorial_body)
    test_program = Program([factorial_func])

    # Transform the program
    transformer = TailCallTransformer()
    transformed_program = transformer.transform_program(test_program)

    print(f"Original program had {len(test_program.functions)} function(s)")
    print(
        f"Transformed program has {len(transformed_program.functions)} function(s)")

    for func in transformed_program.functions:
        params_str = ', '.join(func.parameters)
        print(f"- {func.name}({params_str})")

    return transformed_program


def analyze_function_pattern(function: Function) -> Dict[str, Any]:
    """
    Analyze a function to determine if it matches the transformable pattern.

    Args:
        function: The function to analyze

    Returns:
        Dictionary with analysis results including whether it can be transformed
    """
    transformer = TailCallTransformer()
    pattern_info = transformer._match_pattern(function)

    result = {
        'function_name': function.name,
        'can_transform': pattern_info is not None,
        'reason': None
    }

    if pattern_info is None:
        # Provide detailed analysis of why it can't be transformed
        if len(function.parameters) not in [1, 2]:
            result['reason'] = f"Function has {len(function.parameters)} parameters, expected 1 or 2"
        elif len(function.body.statements) != 1:
            result['reason'] = f"Function body has {len(function.body.statements)} statements, expected 1"
        else:
            stmt = function.body.statements[0]
            if not isinstance(stmt, (IfStatement, ReturnStatement)):
                result['reason'] = f"Main statement is {type(stmt).__name__}, expected IfStatement or ReturnStatement"
            else:
                result['reason'] = "Function structure doesn't match expected recursive pattern"
    else:
        result['pattern_info'] = {
            'main_parameter': pattern_info['main_param'],
            'operator': pattern_info['operator'],
            'base_value': str(pattern_info['base_value']),
            'initial_accumulator': str(pattern_info['initial_accumulator_value'])
        }

    return result


if __name__ == "__main__":
    print("TailCallTransformer Demo")
    print("=" * 40)

    try:
        transformed_program = demo_transformation()
        print("\nTransformation completed successfully!")

        # Show some details about the generated functions
        print("\nGenerated Functions:")
        for func in transformed_program.functions:
            print(f"\nFunction: {func.name}")
            print(f"Parameters: {func.parameters}")
            print(f"Body type: {type(func.body.statements[0]).__name__}")

    except Exception as e:
        print(f"Error during transformation: {e}")
        import traceback
        traceback.print_exc()
