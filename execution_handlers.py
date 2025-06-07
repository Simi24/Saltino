"""
Execution Handlers for the Saltino interpreter.
Contains the logic for handling each FrameType.
"""

from execution_frames import ExecutionFrame, FrameType
from execution_environment import Environment
from AST.ASTNodes import *
from AST.ASTsymbol_table import SymbolKind
from errors.runtime_errors import SaltinoRuntimeError
from typing import Any


def execute_function_frame(frame: ExecutionFrame, interpreter):
    """Esegue un frame di chiamata di funzione."""
    function = frame.state['function']

    if not frame.state['body_executed']:
        # Eseguiamo il corpo della funzione
        interpreter.push_frame(
            FrameType.BLOCK, function.body, frame.environment)
    else:
        # Il corpo è stato eseguito, completiamo il frame
        result = frame.state.get('body_result')
        frame.result = result
        frame.completed = True


def execute_block_frame(frame: ExecutionFrame, interpreter):
    """Esegue un frame di blocco."""
    block = frame.node
    statements = block.statements
    current_index = frame.state['current_statement_index']

    if current_index < len(statements):
        # Eseguiamo la prossima statement
        stmt = statements[current_index]
        push_statement_frame(stmt, frame.environment, interpreter)
    else:
        # Tutte le statement sono state eseguite
        results = frame.state['statements_results']
        # Il risultato del blocco è l'ultimo valore calcolato
        frame.result = results[-1] if results else None
        frame.completed = True


def push_statement_frame(stmt: ASTNode, environment: Environment, interpreter):
    """Pusha il frame appropriato per una statement."""
    if isinstance(stmt, Assignment):
        interpreter.push_frame(FrameType.ASSIGNMENT, stmt, environment)
    elif isinstance(stmt, IfStatement):
        interpreter.push_frame(FrameType.IF_STATEMENT, stmt, environment)
    elif isinstance(stmt, ReturnStatement):
        interpreter.push_frame(FrameType.RETURN, stmt, environment)
    elif isinstance(stmt, Block):
        interpreter.push_frame(FrameType.BLOCK, stmt, environment)
    else:
        # È un'espressione o condizione
        if is_condition_node(stmt):
            interpreter.push_frame(FrameType.CONDITION, stmt, environment)
        else:
            interpreter.push_frame(FrameType.EXPRESSION, stmt, environment)


def is_condition_node(node: ASTNode) -> bool:
    """Determina se un nodo è una condizione."""
    return isinstance(node, (BooleanLiteral, BinaryCondition,
                             UnaryCondition, ComparisonCondition))


def execute_expression_frame(frame: ExecutionFrame, interpreter):
    """Esegue un frame di espressione."""
    node = frame.node

    # Gestione dei diversi tipi di espressione
    if isinstance(node, IntegerLiteral):
        frame.result = node.value
        frame.completed = True
    elif isinstance(node, BooleanLiteral):
        frame.result = node.value
        frame.completed = True
    elif isinstance(node, Identifier):
        try:
            # Usa il nome univoco dalla symbol table per accedere alla variabile
            unique_name = frame.environment.get_unique_name(
                node, frame.semantic_analyzer)
            frame.result = frame.environment.get_variable(unique_name)
            frame.completed = True
        except SaltinoRuntimeError as e:
            # Se non è una variabile, potrebbe essere una funzione
            try:
                function = frame.environment.get_function(node.name)
                frame.result = function
                frame.completed = True
            except SaltinoRuntimeError:
                # Controlla se è un caso di variable shadowing (UnboundLocalError)
                if "unique name" in str(e):
                    raise SaltinoRuntimeError(
                        f"UnboundLocalError: cannot access local variable '{node.name}' "
                        f"where it is not associated with a value. "
                        f"(Variable '{node.name}' is assigned in this scope, making it local, "
                        f"but it's used before assignment)")
                else:
                    raise SaltinoRuntimeError(
                        f"Undefined variable or function: {node.name}")
    elif isinstance(node, EmptyList):
        frame.result = []
        frame.completed = True
    elif isinstance(node, BinaryExpression):
        execute_binary_expression(frame, interpreter)
    elif isinstance(node, UnaryExpression):
        execute_unary_expression(frame, interpreter)
    elif isinstance(node, FunctionCall):
        execute_function_call_expression(frame, interpreter)
    else:
        raise SaltinoRuntimeError(f"Unknown expression type: {type(node)}")


def execute_binary_expression(frame: ExecutionFrame, interpreter):
    """Esegue un'espressione binaria."""
    expr = frame.node
    operands_evaluated = frame.state['operands_evaluated']
    current_index = frame.state['current_operand_index']

    if current_index == 0:
        # Valutiamo l'operando sinistro
        if is_condition_node(expr.left):
            interpreter.push_frame(FrameType.CONDITION,
                                   expr.left, frame.environment)
        else:
            interpreter.push_frame(FrameType.EXPRESSION,
                                   expr.left, frame.environment)
    elif current_index == 1:
        # Valutiamo l'operando destro
        if is_condition_node(expr.right):
            interpreter.push_frame(FrameType.CONDITION,
                                   expr.right, frame.environment)
        else:
            interpreter.push_frame(FrameType.EXPRESSION,
                                   expr.right, frame.environment)
    else:
        # Entrambi gli operandi sono stati valutati
        left_value = operands_evaluated[0]
        right_value = operands_evaluated[1]

        if expr.operator in interpreter.binary_operators:
            frame.result = interpreter.binary_operators[expr.operator](
                left_value, right_value)
        else:
            raise SaltinoRuntimeError(
                f"Unknown binary operator: {expr.operator}")

        frame.completed = True


def execute_unary_expression(frame: ExecutionFrame, interpreter):
    """Esegue un'espressione unaria."""
    expr = frame.node
    operands_evaluated = frame.state['operands_evaluated']
    current_index = frame.state['current_operand_index']

    if current_index == 0:
        # Valutiamo l'operando
        if is_condition_node(expr.operand):
            interpreter.push_frame(FrameType.CONDITION,
                                   expr.operand, frame.environment)
        else:
            interpreter.push_frame(FrameType.EXPRESSION,
                                   expr.operand, frame.environment)
    else:
        # L'operando è stato valutato
        operand_value = operands_evaluated[0]

        if expr.operator in interpreter.unary_operators:
            frame.result = interpreter.unary_operators[expr.operator](
                operand_value)
        else:
            raise SaltinoRuntimeError(
                f"Unknown unary operator: {expr.operator}")

        frame.completed = True


def execute_function_call_expression(frame: ExecutionFrame, interpreter):
    """Esegue una chiamata di funzione all'interno di un'espressione."""
    call = frame.node

    if not frame.state.get('function_evaluated', False):
        # Prima valutiamo l'espressione del callee (potrebbe essere una variabile che contiene una funzione)
        if is_condition_node(call.function):
            interpreter.push_frame(FrameType.CONDITION,
                                   call.function, frame.environment)
        else:
            interpreter.push_frame(FrameType.EXPRESSION,
                                   call.function, frame.environment)
        frame.state['current_phase'] = 'evaluating_function'
        frame.state['arguments_to_evaluate'] = call.arguments[:]
        frame.state['arguments_evaluated'] = []
        frame.state['current_arg_index'] = 0
        return

    if not frame.state.get('function_resolved', False):
        # Il callee è stato valutato, ora determiniamo se è una funzione valida
        function_value = frame.state['function_value']

        # Verifichiamo se è un oggetto Function
        if isinstance(function_value, Function):
            frame.state['function'] = function_value
            frame.state['function_resolved'] = True
        else:
            raise SaltinoRuntimeError(
                f"Cannot call non-function value of type {type(function_value).__name__}"
            )

    # Valutiamo gli argomenti
    args_evaluated = frame.state['arguments_evaluated']
    current_index = frame.state['current_arg_index']
    args_to_evaluate = frame.state['arguments_to_evaluate']

    if current_index < len(args_to_evaluate):
        # Valutiamo il prossimo argomento
        arg = args_to_evaluate[current_index]
        if is_condition_node(arg):
            interpreter.push_frame(FrameType.CONDITION, arg, frame.environment)
        else:
            interpreter.push_frame(FrameType.EXPRESSION,
                                   arg, frame.environment)
        frame.state['current_phase'] = 'evaluating_arguments'
    elif not frame.state.get('function_called', False):
        # Tutti gli argomenti sono stati valutati, chiamiamo la funzione
        function = frame.state['function']

        # Verifichiamo il numero di argomenti
        if len(args_evaluated) != len(function.parameters):
            raise SaltinoRuntimeError(
                f"Function '{function.name}' expects {len(function.parameters)} arguments, "
                f"got {len(args_evaluated)}"
            )

        # Creiamo un nuovo ambiente per la funzione
        function_env = interpreter._create_new_environment(
            interpreter.global_env)

        # Binding dei parametri usando i nomi univoci dalla symbol table
        function_scope = interpreter.semantic_analyzer.get_node_info(
            function, 'scope')
        if function_scope:
            for param, arg in zip(function.parameters, args_evaluated):
                try:
                    param_info = function_scope.lookup_local(param)
                    if param_info and param_info.kind == SymbolKind.PARAMETER:
                        function_env.define_variable(
                            param_info.unique_name, arg)
                    else:
                        raise SaltinoRuntimeError(
                            f"Parameter '{param}' not found in function scope")
                except ValueError:
                    raise SaltinoRuntimeError(
                        f"Parameter '{param}' not found in symbol table")
        else:
            raise SaltinoRuntimeError(
                f"No scope information for function '{function.name}'")

        # Eseguiamo la funzione
        func_frame = interpreter.push_frame(
            FrameType.FUNCTION_CALL, function, function_env)
        func_frame.state['function'] = function
        func_frame.state['body_executed'] = False

        frame.state['function_called'] = True
        frame.state['current_phase'] = 'executing_function'
    # Se arriviamo qui e la funzione è stata chiamata, il risultato sarà gestito da _handle_child_result


def execute_condition_frame(frame: ExecutionFrame, interpreter):
    """Esegue un frame di condizione."""
    node = frame.node

    if isinstance(node, BooleanLiteral):
        frame.result = node.value
        frame.completed = True
    elif isinstance(node, Identifier):
        try:
            # Usa il nome univoco dalla symbol table per accedere alla variabile
            unique_name = frame.environment.get_unique_name(
                node, frame.semantic_analyzer)
            value = frame.environment.get_variable(unique_name)
            # Verifica che il valore sia un booleano
            if type(value) is not bool:
                raise SaltinoRuntimeError(
                    f"Variable '{node.name}' used in condition must be boolean, got {type(value).__name__}")
            frame.result = value
            frame.completed = True
        except SaltinoRuntimeError as e:
            raise SaltinoRuntimeError(
                f"Error accessing variable '{node.name}': {e.message}")
    elif isinstance(node, BinaryCondition):
        execute_binary_condition(frame, interpreter)
    elif isinstance(node, UnaryCondition):
        execute_unary_condition(frame, interpreter)
    elif isinstance(node, ComparisonCondition):
        execute_comparison_condition(frame, interpreter)
    elif isinstance(node, FunctionCall):
        # Chiamata di funzione usata come condizione - deve restituire un booleano
        execute_function_call_in_condition(frame, interpreter)
    else:
        raise SaltinoRuntimeError(f"Unknown condition type: {type(node)}")


def execute_binary_condition(frame: ExecutionFrame, interpreter):
    """Esegue una condizione binaria."""
    condition = frame.node
    operands_evaluated = frame.state['operands_evaluated']
    current_index = frame.state['current_operand_index']

    if current_index == 0:
        # Valutiamo l'operando sinistro
        interpreter.push_frame(FrameType.CONDITION,
                               condition.left, frame.environment)
    elif current_index == 1:
        # Valutazione short-circuit per and e or
        left_value = operands_evaluated[0]

        # Controllo di tipo per il primo operando
        if type(left_value) is not bool:
            raise SaltinoRuntimeError(
                f"Logical operators can only operate on boolean values, got {type(left_value).__name__}")

        if condition.operator == 'and' and not left_value:
            frame.result = False
            frame.completed = True
            return
        elif condition.operator == 'or' and left_value:
            frame.result = True
            frame.completed = True
            return

        # Valutiamo l'operando destro
        interpreter.push_frame(FrameType.CONDITION,
                               condition.right, frame.environment)
    else:
        # Entrambi gli operandi sono stati valutati
        left_value = operands_evaluated[0]
        right_value = operands_evaluated[1]

        if condition.operator in interpreter.logical_operators:
            frame.result = interpreter.logical_operators[condition.operator](
                left_value, right_value)
        else:
            raise SaltinoRuntimeError(
                f"Unknown logical operator: {condition.operator}")

        frame.completed = True


def execute_unary_condition(frame: ExecutionFrame, interpreter):
    """Esegue una condizione unaria."""
    condition = frame.node
    operands_evaluated = frame.state['operands_evaluated']
    current_index = frame.state['current_operand_index']

    if current_index == 0:
        # Valutiamo l'operando
        interpreter.push_frame(FrameType.CONDITION,
                               condition.operand, frame.environment)
    else:
        # L'operando è stato valutato
        operand_value = operands_evaluated[0]

        if condition.operator == '!':
            # Controllo di tipo: negazione può operare solo su valori booleani
            if type(operand_value) is not bool:
                raise SaltinoRuntimeError(
                    f"Logical negation can only operate on boolean values, got {type(operand_value).__name__}")
            frame.result = not operand_value
        else:
            raise SaltinoRuntimeError(
                f"Unknown unary logical operator: {condition.operator}")

        frame.completed = True


def execute_comparison_condition(frame: ExecutionFrame, interpreter):
    """Esegue una condizione di confronto."""
    comparison = frame.node
    operands_evaluated = frame.state['operands_evaluated']
    current_index = frame.state['current_operand_index']

    if current_index == 0:
        # Valutiamo l'operando sinistro
        interpreter.push_frame(FrameType.EXPRESSION,
                               comparison.left, frame.environment)
    elif current_index == 1:
        # Valutiamo l'operando destro
        interpreter.push_frame(FrameType.EXPRESSION,
                               comparison.right, frame.environment)
    else:
        # Entrambi gli operandi sono stati valutati
        left_value = operands_evaluated[0]
        right_value = operands_evaluated[1]

        if comparison.operator in interpreter.comparison_operators:
            frame.result = interpreter.comparison_operators[comparison.operator](
                left_value, right_value)
        else:
            raise SaltinoRuntimeError(
                f"Unknown comparison operator: {comparison.operator}")

        frame.completed = True


def execute_function_call_in_condition(frame: ExecutionFrame, interpreter):
    """Esegue una chiamata di funzione usata come condizione."""
    call = frame.node

    if not frame.state.get('function_evaluated', False):
        # Prima valutiamo l'espressione del callee
        if is_condition_node(call.function):
            interpreter.push_frame(FrameType.CONDITION,
                                   call.function, frame.environment)
        else:
            interpreter.push_frame(FrameType.EXPRESSION,
                                   call.function, frame.environment)
        frame.state['current_phase'] = 'evaluating_function'
        frame.state['arguments_to_evaluate'] = call.arguments[:]
        frame.state['arguments_evaluated'] = []
        frame.state['current_arg_index'] = 0
        return

    if not frame.state.get('function_resolved', False):
        # Il callee è stato valutato, verifichiamo che sia una funzione
        function_value = frame.state['function_value']

        if isinstance(function_value, Function):
            frame.state['function'] = function_value
            frame.state['function_resolved'] = True
        else:
            raise SaltinoRuntimeError(
                f"Cannot call non-function value of type {type(function_value).__name__}"
            )

    # Valutiamo gli argomenti
    args_evaluated = frame.state['arguments_evaluated']
    current_index = frame.state['current_arg_index']
    args_to_evaluate = frame.state['arguments_to_evaluate']

    if current_index < len(args_to_evaluate):
        # Valutiamo il prossimo argomento
        arg = args_to_evaluate[current_index]
        if is_condition_node(arg):
            interpreter.push_frame(FrameType.CONDITION, arg, frame.environment)
        else:
            interpreter.push_frame(FrameType.EXPRESSION,
                                   arg, frame.environment)
        frame.state['current_phase'] = 'evaluating_arguments'
    elif not frame.state.get('function_called', False):
        # Tutti gli argomenti sono stati valutati, chiamiamo la funzione
        function = frame.state['function']

        # Verifichiamo il numero di argomenti
        if len(args_evaluated) != len(function.parameters):
            raise SaltinoRuntimeError(
                f"Function '{function.name}' expects {len(function.parameters)} arguments, "
                f"got {len(args_evaluated)}"
            )

        # Creiamo un nuovo ambiente per la funzione
        function_env = interpreter._create_new_environment(
            interpreter.global_env)

        # Binding dei parametri
        function_scope = interpreter.semantic_analyzer.get_node_info(
            function, 'scope')
        if function_scope:
            for param, arg in zip(function.parameters, args_evaluated):
                try:
                    param_info = function_scope.lookup_local(param)
                    if param_info and param_info.kind == SymbolKind.PARAMETER:
                        function_env.define_variable(
                            param_info.unique_name, arg)
                    else:
                        raise SaltinoRuntimeError(
                            f"Parameter '{param}' not found in function scope")
                except ValueError:
                    raise SaltinoRuntimeError(
                        f"Parameter '{param}' not found in symbol table")
        else:
            raise SaltinoRuntimeError(
                f"No scope information for function '{function.name}'")

        # Eseguiamo la funzione
        func_frame = interpreter.push_frame(
            FrameType.FUNCTION_CALL, function, function_env)
        func_frame.state['function'] = function
        func_frame.state['body_executed'] = False

        frame.state['function_called'] = True
        frame.state['current_phase'] = 'executing_function'
    else:
        # La funzione è stata chiamata, il risultato è stato impostato da _handle_child_result
        result = frame.state.get('function_result')
        # Verifichiamo che il risultato sia un booleano
        if type(result) is not bool:
            raise SaltinoRuntimeError(
                f"Function used in condition must return boolean, got {type(result).__name__}")
        frame.result = result
        frame.completed = True


def execute_if_frame(frame: ExecutionFrame, interpreter):
    """Esegue un frame di statement if."""
    if_stmt = frame.node

    if not frame.state['condition_evaluated']:
        # Valutiamo la condizione
        interpreter.push_frame(FrameType.CONDITION,
                               if_stmt.condition, frame.environment)
    elif not frame.state['branch_executed']:
        # La condizione è stata valutata, eseguiamo il ramo appropriato
        condition_result = frame.state['condition_result']

        if condition_result:
            # Eseguiamo il ramo then
            interpreter.push_frame(FrameType.BLOCK,
                                   if_stmt.then_block, frame.environment)
        elif if_stmt.else_block:
            # Eseguiamo il ramo else
            interpreter.push_frame(FrameType.BLOCK,
                                   if_stmt.else_block, frame.environment)
        else:
            # Nessun ramo else, completiamo con None
            frame.result = None
            frame.completed = True
    else:
        # Il ramo è stato eseguito
        frame.result = frame.state.get('branch_result')
        frame.completed = True


def execute_assignment_frame(frame: ExecutionFrame, interpreter):
    """Esegue un frame di assegnamento usando i nomi univoci dalla symbol table."""
    assignment = frame.node

    if not frame.state.get('value_evaluated', False):
        # Valutiamo il valore da assegnare
        if is_condition_node(assignment.value):
            interpreter.push_frame(FrameType.CONDITION,
                                   assignment.value, frame.environment)
        else:
            interpreter.push_frame(FrameType.EXPRESSION,
                                   assignment.value, frame.environment)
    else:
        # Il valore è stato valutato, eseguiamo l'assegnamento usando il nome univoco
        value = frame.state['value']

        # Ottiene il nome univoco dalla symbol table
        unique_name = frame.environment.get_unique_name(
            assignment, frame.semantic_analyzer)
        frame.environment.set_variable(unique_name, value)

        frame.result = value
        frame.completed = True


def execute_return_frame(frame: ExecutionFrame, interpreter):
    """Esegue un frame di return con supporto TCO."""
    return_stmt = frame.node

    # Controlla per l'Ottimizzazione delle Tail Call
    is_tail_call = False
    if isinstance(return_stmt.value, FunctionCall) and interpreter.semantic_analyzer:
        is_tail_call = interpreter.semantic_analyzer.get_node_info(
            return_stmt.value, 'is_potential_tail_call', False)

    if is_tail_call:
        # TCO: processo multi-fase
        if interpreter.debug_mode:
            print(
                f"[TCO] Tail call rilevata nel return statement: {return_stmt.value}")
        if 'tco_phase' not in frame.state:
            # Fase 1: Valuta il callee (oggetto funzione)
            frame.state['tco_phase'] = 'eval_callee'
            frame.state['tail_call_function_value'] = None
            frame.state['tail_call_evaluated_args'] = []
            frame.state['tail_call_current_arg_index'] = 0
            if interpreter.debug_mode:
                print(
                    f"[TCO] Fase 1: Valutazione del callee per tail call: {return_stmt.value.function}")
            interpreter.push_frame(FrameType.EXPRESSION,
                                   return_stmt.value.function, frame.environment)
        elif frame.state['tco_phase'] == 'eval_args':
            # Wait for arguments to be evaluated in _handle_child_result
            args = return_stmt.value.arguments
            idx = frame.state['tail_call_current_arg_index']
            if idx < len(args):
                arg = args[idx]
                if interpreter.debug_mode:
                    print(f"[TCO] Valutazione argomento {idx}: {arg}")
                if is_condition_node(arg):
                    interpreter.push_frame(FrameType.CONDITION,
                                           arg, frame.environment)
                else:
                    interpreter.push_frame(FrameType.EXPRESSION,
                                           arg, frame.environment)
            # else: gestito da tco_phase 'ready_to_tailcall' quando tutti gli argomenti sono pronti
        elif frame.state['tco_phase'] == 'ready_to_tailcall':
            if interpreter.debug_mode:
                print(
                    f"[TCO] Phase 3: Performing stack manipulation for tail call.")
            # Phase 3: Stack manipulation for TCO
            # Pop RETURN, BLOCK, FUNCTION_CALL frames
            # (RETURN is current frame)
            interpreter.pop_frame()  # Pop RETURN
            # Pop BLOCK (function body)
            if interpreter.execution_stack and interpreter.execution_stack[-1].frame_type == FrameType.BLOCK:
                interpreter.pop_frame()
            # Pop FUNCTION_CALL (current function)
            if interpreter.execution_stack and interpreter.execution_stack[-1].frame_type == FrameType.FUNCTION_CALL:
                interpreter.pop_frame()
            # Prepare new environment for the tail call
            function_obj = frame.state['tail_call_function_value']
            args = frame.state['tail_call_evaluated_args']
            function_env = interpreter._create_new_environment(
                interpreter.global_env)
            # Bind parameters using semantic info
            if interpreter.semantic_analyzer:
                function_scope = interpreter.semantic_analyzer.get_node_info(
                    function_obj, 'scope')
                if function_scope:
                    for param, arg in zip(function_obj.parameters, args):
                        try:
                            param_info = function_scope.lookup_local(param)
                            if param_info and param_info.kind == SymbolKind.PARAMETER:
                                function_env.define_variable(
                                    param_info.unique_name, arg)
                                if interpreter.debug_mode:
                                    print(
                                        f"[TCO] Bound parameter {param} (unique: {param_info.unique_name}) = {arg}")
                            else:
                                raise SaltinoRuntimeError(
                                    f"Parameter '{param}' not found in function scope")
                        except ValueError:
                            raise SaltinoRuntimeError(
                                f"Parameter '{param}' not found in symbol table")
                else:
                    raise SaltinoRuntimeError(
                        f"No scope information for function '{function_obj.name}'")
            # Push new FUNCTION_CALL frame for the tail call
            interpreter.tail_call_count += 1  # Count successful tail call optimization
            if interpreter.debug_mode:
                print(
                    f"[TCO] Pushing new FUNCTION_CALL frame for tail call: {function_obj.name}({args})")
            func_frame = interpreter.push_frame(
                FrameType.FUNCTION_CALL, function_obj, function_env)
            func_frame.state['function'] = function_obj
            func_frame.state['body_executed'] = False
            # Mark this frame as completed
            frame.completed = True
        else:
            # Should not reach here
            raise SaltinoRuntimeError("Invalid TCO phase in return frame")
    else:
        # Logica originale (non-tail call)
        if not frame.state.get('value_evaluated', False):
            # Valutiamo il valore del return
            if is_condition_node(return_stmt.value):
                interpreter.push_frame(FrameType.CONDITION,
                                       return_stmt.value, frame.environment)
            else:
                interpreter.push_frame(FrameType.EXPRESSION,
                                       return_stmt.value, frame.environment)
        else:
            # Il valore è stato valutato
            return_value = frame.state['return_value']

            # Dobbiamo propagare il return fino al frame della funzione
            # Rimuoviamo tutti i frame fino alla funzione
            while interpreter.execution_stack:
                current = interpreter.pop_frame()
                if current.frame_type == FrameType.FUNCTION_CALL:
                    # Impostiamo il risultato e completiamo la funzione
                    current.result = return_value
                    current.completed = True
                    interpreter.execution_stack.append(current)
                    break

            frame.completed = True
