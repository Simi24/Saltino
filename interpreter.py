#!/usr/bin/env python3
"""
Refactored Iterative Interpreter for the Saltino language.

This interpreter uses a stack of execution frames to eliminate recursion
from function calls and provides iterative execution of AST-represented code.
"""

from AST.ASTNodes import *
from AST.semantic_analyzer import SemanticAnalyzer
from AST.ASTsymbol_table import SymbolKind
from errors.runtime_errors import SaltinoRuntimeError
from execution_frames import ExecutionFrame, FrameType
from execution_environment import Environment
from saltino_operators import SaltinoOperators
from typing import Any, List, Optional
import execution_handlers as handlers
from io_handler import get_main_arguments
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class IterativeSaltinoInterpreter:
    """
    Refactored Iterative Interpreter for the Saltino language with semantic analysis support.

    Uses a stack of execution frames to eliminate recursion and handle execution iteratively.
    Integrates with SemanticAnalyzer to use unique names and scope information.
    """

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.global_env = Environment(scope_name="global")
        self.execution_stack: List[ExecutionFrame] = []
        self.result_stack: List[Any] = []
        # Semantic analyzer
        self.semantic_analyzer: Optional[SemanticAnalyzer] = None

        # Dispatch table for binary operations
        self.binary_operators = SaltinoOperators.get_binary_operators()

        # Dispatch table for unary operations
        self.unary_operators = SaltinoOperators.get_unary_operators()

        # Dispatch table for comparison operations
        self.comparison_operators = SaltinoOperators.get_comparison_operators()

        # Dispatch table for logical operations
        self.logical_operators = SaltinoOperators.get_logical_operators()

        # Frame handler dispatch table
        self.frame_handlers = {
            FrameType.FUNCTION_CALL: handlers.execute_function_frame,
            FrameType.BLOCK: handlers.execute_block_frame,
            FrameType.EXPRESSION: handlers.execute_expression_frame,
            FrameType.CONDITION: handlers.execute_condition_frame,
            FrameType.IF_STATEMENT: handlers.execute_if_frame,
            FrameType.ASSIGNMENT: handlers.execute_assignment_frame,
            FrameType.RETURN: handlers.execute_return_frame,
        }

    def _create_new_environment(self, parent: Environment = None) -> Environment:
        """Creates a new environment with the specified parent."""
        return Environment(parent or self.global_env)

    def push_frame(self, frame_type: FrameType, node: ASTNode, environment: Environment):
        """Adds a new frame to the execution stack with semantic analyzer reference."""
        frame = ExecutionFrame(
            frame_type, node, environment, self.semantic_analyzer)
        self.execution_stack.append(frame)
        return frame

    def pop_frame(self) -> Optional[ExecutionFrame]:
        """Removes and returns the last frame from the stack."""
        if self.execution_stack:
            return self.execution_stack.pop()
        return None

    def current_frame(self) -> Optional[ExecutionFrame]:
        """Returns the current frame without removing it."""
        if self.execution_stack:
            return self.execution_stack[-1]
        return None

    def execute_program(self, program: Program) -> Any:
        """Executes a Saltino program iteratively."""
        # Semantic analysis has already been performed in the parser
        # So we can proceed directly with execution

        # Register all functions in the global environment
        for function in program.functions:
            self.global_env.define_function(function.name, function)

        # Find and execute the main function
        try:
            main_function = self.global_env.get_function('main')
        except SaltinoRuntimeError:
            raise SaltinoRuntimeError("No main function found")

        # If main has parameters, ask the user to enter them
        args = get_main_arguments(main_function)
        return self.call_function(main_function, args)

    def call_function(self, function: Function, arguments: List[Any]) -> Any:
        """Starts a function call by pushing a frame onto the stack."""
        if len(arguments) != len(function.parameters):
            raise SaltinoRuntimeError(
                f"Function '{function.name}' expects {len(function.parameters)} arguments, "
                f"got {len(arguments)}"
            )

        # Create a new environment for the function
        function_env = self._create_new_environment(self.global_env)

        # Parameter binding using unique names from symbol table
        if self.semantic_analyzer:
            function_scope = self.semantic_analyzer.get_node_info(function, 'scope')
            if function_scope:
                for param, arg in zip(function.parameters, arguments):
                    try:
                        param_info = function_scope.lookup_local(param)
                        if param_info and param_info.kind == SymbolKind.PARAMETER:
                            function_env.define_variable(param_info.unique_name, arg)
                        else:
                            raise SaltinoRuntimeError(
                                f"Parameter '{param}' not found in function scope")
                    except ValueError:
                        raise SaltinoRuntimeError(
                            f"Parameter '{param}' not found in symbol table")
            else:
                raise SaltinoRuntimeError(
                    f"No scope information for function '{function.name}'")
        else:
            # Fallback to original names if no semantic analyzer
            for param, arg in zip(function.parameters, arguments):
                function_env.define_variable(param, arg)

        # Push the function frame
        frame = self.push_frame(FrameType.FUNCTION_CALL,
                                function, function_env)
        frame.state['function'] = function
        frame.state['body_executed'] = False

        # Start iterative execution
        return self.execute()

    def execute(self) -> Any:
        """Main iterative execution loop."""
        while self.execution_stack:
            frame = self.current_frame()

            if frame.completed:
                # Frame is completed, propagate the result
                result = frame.result
                self.pop_frame()

                # If there's a parent frame, pass the result to it
                if self.execution_stack:
                    parent_frame = self.current_frame()
                    self._handle_child_result(parent_frame, result)
                else:
                    # No more frames, return the final result
                    return result
                continue

            # Process the current frame based on its type
            try:
                handler = self.frame_handlers.get(frame.frame_type)
                if handler:
                    handler(frame, self)
                else:
                    raise SaltinoRuntimeError(f"Unknown frame type: {frame.frame_type}")
            except Exception as e:
                # Error handling - propagate the error
                if isinstance(e, SaltinoRuntimeError):
                    raise e
                else:
                    raise SaltinoRuntimeError(f"Internal error: {str(e)}")

        return None

    def _handle_child_result(self, parent_frame: ExecutionFrame, result: Any):
        """Handles the result of a child frame in the parent frame."""
        if parent_frame.frame_type == FrameType.FUNCTION_CALL:
            # Function body has been executed
            parent_frame.state['body_result'] = result
            parent_frame.state['body_executed'] = True
        elif parent_frame.frame_type == FrameType.BLOCK:
            # A statement in the block has been executed
            parent_frame.state['statements_results'].append(result)
            parent_frame.state['current_statement_index'] += 1
        elif parent_frame.frame_type == FrameType.EXPRESSION:
            # Handle function calls and other expressions
            if isinstance(parent_frame.node, FunctionCall):
                # Handle different phases of function call
                current_phase = parent_frame.state.get(
                    'current_phase', 'evaluating_function')

                if current_phase == 'evaluating_function':
                    # Function has been evaluated
                    parent_frame.state['function_value'] = result
                    parent_frame.state['function_evaluated'] = True
                elif current_phase == 'evaluating_arguments':
                    # An argument has been evaluated
                    parent_frame.state['arguments_evaluated'].append(result)
                    parent_frame.state['current_arg_index'] += 1
                elif current_phase == 'executing_function':
                    # Result of function call
                    parent_frame.result = result
                    parent_frame.completed = True
            else:
                # An operand has been evaluated for another expression
                parent_frame.state['operands_evaluated'].append(result)
                parent_frame.state['current_operand_index'] += 1
        elif parent_frame.frame_type == FrameType.CONDITION:
            # A condition operand has been evaluated
            if isinstance(parent_frame.node, FunctionCall):
                # Special case: function call used as condition
                current_phase = parent_frame.state.get(
                    'current_phase', 'evaluating_function')

                if current_phase == 'evaluating_function':
                    # Function has been evaluated
                    parent_frame.state['function_value'] = result
                    parent_frame.state['function_evaluated'] = True
                elif current_phase == 'evaluating_arguments':
                    # An argument has been evaluated
                    parent_frame.state['arguments_evaluated'].append(result)
                    parent_frame.state['current_arg_index'] += 1
                elif current_phase == 'executing_function':
                    # Result of function call used as condition
                    parent_frame.state['function_result'] = result
            else:
                # Normal operand of a condition
                parent_frame.state['operands_evaluated'].append(result)
                parent_frame.state['current_operand_index'] += 1
        elif parent_frame.frame_type == FrameType.IF_STATEMENT:
            if not parent_frame.state['condition_evaluated']:
                # Condition has been evaluated
                parent_frame.state['condition_result'] = result
                parent_frame.state['condition_evaluated'] = True
            else:
                # Branch has been executed
                parent_frame.state['branch_result'] = result
                parent_frame.state['branch_executed'] = True
        elif parent_frame.frame_type == FrameType.ASSIGNMENT:
            # Assignment value has been evaluated
            parent_frame.state['value'] = result
            parent_frame.state['value_evaluated'] = True
        elif parent_frame.frame_type == FrameType.RETURN:
            # Return value has been evaluated
            parent_frame.state['return_value'] = result
            parent_frame.state['value_evaluated'] = True
