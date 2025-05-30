from dataclasses import dataclass
from typing import Any, Optional, Dict, List
from enum import Enum
from AST.ASTNodes import ASTNode


class SymbolKind(Enum):
    VARIABLE = "variable"
    FUNCTION = "function"
    PARAMETER = "parameter"

@dataclass
class SymbolInfo:
    name: str
    kind: SymbolKind
    scope_level: int
    unique_name: str
    node_ref: Optional[ASTNode] = None  # Riferimento al nodo AST originale

class SymbolTable:
    NUM_INSTANCES = 0

    def __init__(self, parent=None, scope_name="global"):
        self.num = SymbolTable.NUM_INSTANCES
        SymbolTable.NUM_INSTANCES += 1
        self.parent = parent
        self.scope_name = scope_name
        self.symbol2info: Dict[str, SymbolInfo] = {}
        self.level = 0 if parent is None else parent.level + 1
        self.children: List['SymbolTable'] = []  # Lista dei scope figli

    def bind(self, symbol: str, kind: SymbolKind, node_ref=None):
        """Associa un simbolo nel scope corrente"""
        unique_name = f"{symbol}_{self.num}_{len(self.symbol2info)}"
        info = SymbolInfo(
            name=symbol,
            kind=kind,
            scope_level=self.level,
            unique_name=unique_name,
            node_ref=node_ref
        )
        self.symbol2info[symbol] = info
        return info

    def lookup(self, symbol: str) -> SymbolInfo:
        """Cerca un simbolo risalendo la catena degli scope"""
        if symbol in self.symbol2info:
            return self.symbol2info[symbol]
        if self.parent:
            return self.parent.lookup(symbol)
        raise ValueError(f'Symbol {symbol} not found')

    def lookup_local(self, symbol: str) -> Optional[SymbolInfo]:
        """Cerca un simbolo solo nel scope corrente"""
        return self.symbol2info.get(symbol)

    def enter(self, scope_name="block"):
        """Entra in un nuovo scope"""
        child_scope = SymbolTable(self, scope_name)
        self.children.append(child_scope)  # Aggiungi il figlio alla lista
        return child_scope

    def exit(self):
        """Esce dal scope corrente"""
        if self.parent is None:
            raise ValueError('No containing SymbolTable')
        return self.parent

    def __repr__(self):
        return f'ST[{self.scope_name}_{self.num}]'
