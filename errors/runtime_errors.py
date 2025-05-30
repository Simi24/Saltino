#!/usr/bin/env python3
"""
Eccezioni per l'interprete Saltino.

Questo modulo contiene le definizioni delle eccezioni personalizzate
utilizzate dall'interprete durante l'esecuzione.
"""

from AST.ASTNodes import SourcePosition
from typing import Optional


class SaltinoRuntimeError(Exception):
    """Eccezione per errori di runtime del linguaggio Saltino."""

    def __init__(self, message: str, position: Optional[SourcePosition] = None):
        self.message = message
        self.position = position
        super().__init__(self._format_message())

    def _format_message(self):
        if self.position:
            return f"Runtime Error at {self.position}: {self.message}"
        return f"Runtime Error: {self.message}"
