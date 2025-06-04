#!/usr/bin/env python3
"""
Frame di esecuzione per l'interprete iterativo Saltino.

Questo modulo contiene le definizioni dei frame di esecuzione utilizzati
dallo stack dell'interprete per gestire l'esecuzione iterativa.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class FrameType(Enum):
    """Tipi di frame nello stack di esecuzione."""
    FUNCTION_CALL = "function_call"
    BLOCK = "block"
    EXPRESSION = "expression"
    CONDITION = "condition"
    IF_STATEMENT = "if_statement"
    ASSIGNMENT = "assignment"
    RETURN = "return"


@dataclass
class ExecutionFrame:
    """Frame di esecuzione contenente lo stato di un'operazione."""
    frame_type: FrameType
    node: Any  # ASTNode
    environment: Any  # Environment
    # Riferimento all'analizzatore semantico
    semantic_analyzer: Optional[Any] = None  # SemanticAnalyzer
    state: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    completed: bool = False

    def __post_init__(self):
        # Inizializza lo stato specifico per tipo di frame
        if self.frame_type == FrameType.FUNCTION_CALL:
            self.state.update({
                'function': None,
                'body_executed': False,
                'body_result': None
            })
        elif self.frame_type == FrameType.BLOCK:
            self.state.update({
                'current_statement_index': 0,
                'statements_results': []
            })
        elif self.frame_type == FrameType.EXPRESSION:
            self.state.update({
                'operands_evaluated': [],
                'current_operand_index': 0,
                'arguments_evaluated': [],
                'current_arg_index': 0,
                'function_evaluated': False,
                'function_resolved': False,
                'function_called': False,
                'arguments_to_evaluate': []
            })
        elif self.frame_type == FrameType.CONDITION:
            self.state.update({
                'operands_evaluated': [],
                'current_operand_index': 0,
                'arguments_evaluated': [],
                'current_arg_index': 0,
                'function_evaluated': False,
                'function_resolved': False,
                'function_called': False,
                'arguments_to_evaluate': []
            })
        elif self.frame_type == FrameType.IF_STATEMENT:
            self.state.update({
                'condition_evaluated': False,
                'condition_result': None,
                'branch_executed': False
            })
        elif self.frame_type == FrameType.ASSIGNMENT:
            self.state.update({
                'value_evaluated': False,
                'value': None
            })
        elif self.frame_type == FrameType.RETURN:
            self.state.update({
                'value_evaluated': False,
                'return_value': None
            })