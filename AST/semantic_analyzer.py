from antlr4 import InputStream, CommonTokenStream
from AST.ASTsymbol_table import SymbolTable, SymbolKind
from AST.ASTNodes import *
from AST.ASTVisitor import build_ast, print_ast
from Grammatica.SaltinoLexer import SaltinoLexer
from Grammatica.SaltinoParser import SaltinoParser
import sys
import os
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

# Add the workspace root to the Python path
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, workspace_root)


class SemanticError(Exception):
    """Eccezione base per errori semantici"""
    pass


class UnboundLocalError(SemanticError):
    """Eccezione per variabili locali non inizializzate"""
    pass


class SemanticAnalyzer:
    """Analizzatore semantico che implementa il pattern Visitor per decorare l'AST"""

    def __init__(self):
        self.global_scope = SymbolTable(scope_name="global")
        self.current_scope = self.global_scope
        self.symbol_counter = 0

        # Dizionario per memorizzare le informazioni semantiche sui nodi
        # Chiave: id(nodo), Valore: informazioni semantiche
        self.node_info: Dict[int, Dict[str, Any]] = {}

    def analyze(self, program: Program):
        """Punto di ingresso per l'analisi semantica"""
        try:
            program.accept(self)
            print("✅ Analisi semantica completata con successo!")
            return True
        except UnboundLocalError as e:
            print(f"❌ UnboundLocalError: {e}")
            return False
        except SemanticError as e:
            print(f"❌ Errore semantico: {e}")
            return False
        except Exception as e:
            print(f"❌ Errore nell'analisi semantica: {e}")
            return False

    def set_node_info(self, node: ASTNode, **kwargs):
        """Memorizza informazioni semantiche per un nodo"""
        node_id = id(node)
        if node_id not in self.node_info:
            self.node_info[node_id] = {}
        self.node_info[node_id].update(kwargs)

    def get_node_info(self, node: ASTNode, key: str, default=None):
        """Recupera informazioni semantiche di un nodo"""
        node_id = id(node)
        return self.node_info.get(node_id, {}).get(key, default)

    # ==================== VISITOR METHODS ====================

    def visit_program(self, node: Program):
        """Visita il programma principale"""
        self.set_node_info(node, scope=self.current_scope)

        # Prima passa: dichiara tutte le funzioni nel scope globale
        for function in node.functions:
            func_info = self.current_scope.bind(
                function.name, SymbolKind.FUNCTION, function)
            self.set_node_info(function, symbol_info=func_info)
            print(
                f"Dichiarata funzione: {function.name} -> {func_info.unique_name}")

        # Seconda passa: analizza i corpi delle funzioni
        for function in node.functions:
            function.accept(self)

    def visit_function(self, node: Function):
        """Visita una definizione di funzione"""
        print(f"\n--- Analizzando funzione: {node.name} ---")

        # Entra in un nuovo scope per la funzione
        func_scope = self.current_scope.enter(f"function_{node.name}")
        old_scope = self.current_scope
        self.current_scope = func_scope

        self.set_node_info(node, scope=func_scope)

        # Dichiara i parametri nel nuovo scope
        for param in node.parameters:
            param_info = self.current_scope.bind(param, SymbolKind.PARAMETER)
            print(f"  Parametro: {param} -> {param_info.unique_name}")

        # Analizza il corpo della funzione
        node.body.accept(self)

        # Esce dal scope della funzione
        self.current_scope = old_scope
        print(f"--- Fine funzione: {node.name} ---")

    def visit_block(self, node: Block):
        """Visita un blocco di istruzioni
        
        Implementa un approccio a due fasi per rilevare UnboundLocalError:
        1. Prima fase: identifica tutte le variabili che vengono assegnate nel blocco
        2. Seconda fase: analizza le espressioni con la conoscenza delle variabili locali
        """
        # Entra in un nuovo scope per il blocco
        block_scope = self.current_scope.enter("block")
        old_scope = self.current_scope
        self.current_scope = block_scope

        self.set_node_info(node, scope=block_scope)
        print(f"  Entrato nel blocco scope: {block_scope}")

        # FASE 1: Pre-dichiarazione delle variabili locali
        # Identifica tutte le variabili che vengono assegnate in questo blocco
        local_assignments = set()
        self._collect_local_assignments(node.statements, local_assignments)
        
        # Pre-dichiara tutte le variabili locali come "non inizializzate"
        for var_name in local_assignments:
            var_info = self.current_scope.bind(var_name, SymbolKind.VARIABLE, None)
            print(f"  Pre-dichiarata variabile locale: {var_name} -> {var_info.unique_name}")
            # Marca la variabile come non inizializzata
            self.set_node_info(var_info, uninitialized=True)

        # FASE 2: Analisi delle istruzioni
        for statement in node.statements:
            statement.accept(self)

        # Esce dal scope del blocco
        self.current_scope = old_scope
        print(f"  Uscito dal blocco scope: {block_scope}")

    def _collect_local_assignments(self, statements, local_assignments):
        """Raccoglie ricorsivamente tutti i nomi di variabili assegnate nelle statements"""
        for stmt in statements:
            if isinstance(stmt, Assignment):
                local_assignments.add(stmt.variable)
            elif isinstance(stmt, IfStatement):
                # Analizza ricorsivamente i blocchi then/else
                self._collect_local_assignments(stmt.then_block.statements, local_assignments)
                if stmt.else_block:
                    self._collect_local_assignments(stmt.else_block.statements, local_assignments)
            elif isinstance(stmt, Block):
                # Non raccoglie da blocchi annidati - hanno il loro scope
                pass

    def visit_assignment(self, node: Assignment):
        """Visita un assegnamento

        Implementa la semantica Python per gli assegnamenti:
        - Ogni assegnamento crea una nuova variabile locale nel scope corrente se non esiste già
        - Se la variabile esiste già nello stesso scope, la riassegna
        - Se la variabile esiste in uno scope esterno, fa shadowing (crea una nuova variabile locale)

        Questa scelta semantica è stata adottata perché:
        1. È prevedibile: ogni '=' crea/aggiorna una variabile locale
        2. È consistente: comportamento uniforme in tutti i scope
        3. È familiare: stesso comportamento di Python
        4. Evita ambiguità: non serve distinguere tra dichiarazione e assegnamento

        Esempio:
        ```
        x = 10          // Nuova variabile x_scope_0
        {
            x = 20      // Shadowing: nuova variabile x_scope_1 (nasconde x_scope_0)
            x = 30      // Riassegnamento: aggiorna x_scope_1
        }
        x = 40          // Riassegnamento: aggiorna x_scope_0
        ```
        """
        self.set_node_info(node, scope=self.current_scope)

        # Prima analizza il valore da assegnare (RHS)
        node.value.accept(self)

        # Poi gestisce l'assegnamento (LHS)
        existing = self.current_scope.lookup_local(node.variable)
        if existing:
            # Variabile già esiste nel scope corrente
            is_uninitialized = self.get_node_info(existing, 'uninitialized', False)
            if is_uninitialized:
                # Prima volta che viene assegnata - la marchiamo come inizializzata
                self.set_node_info(existing, uninitialized=False)
                print(f"  Inizializzata variabile locale: {node.variable} -> {existing.unique_name}")
            else:
                print(f"  Riassegnamento: {node.variable} -> {existing.unique_name}")
            var_info = existing
        else:
            # Nuova variabile (questo dovrebbe essere raro con il pre-scan)
            var_info = self.current_scope.bind(
                node.variable, SymbolKind.VARIABLE, node)
            print(
                f"  Nuova variabile: {node.variable} -> {var_info.unique_name}")

        self.set_node_info(node, variable_info=var_info)

    def visit_if_statement(self, node: IfStatement):
        """Visita un'istruzione if"""
        self.set_node_info(node, scope=self.current_scope)

        # Analizza la condizione
        node.condition.accept(self)

        # Analizza il blocco then
        node.then_block.accept(self)

        # Analizza il blocco else se presente
        if node.else_block:
            node.else_block.accept(self)

    def visit_return_statement(self, node: ReturnStatement):
        """Visita un'istruzione return"""
        self.set_node_info(node, scope=self.current_scope)
        node.value.accept(self)

    def visit_binary_expression(self, node: BinaryExpression):
        """Visita un'espressione binaria"""
        self.set_node_info(node, scope=self.current_scope)
        node.left.accept(self)
        node.right.accept(self)

    def visit_unary_expression(self, node: UnaryExpression):
        """Visita un'espressione unaria"""
        self.set_node_info(node, scope=self.current_scope)
        node.operand.accept(self)

    def visit_function_call(self, node: FunctionCall):
        """Visita una chiamata di funzione"""
        self.set_node_info(node, scope=self.current_scope)

        # Analizza la funzione (dovrebbe essere un Identifier)
        node.function.accept(self)

        # Analizza tutti gli argomenti
        for arg in node.arguments:
            arg.accept(self)

    def visit_identifier(self, node: Identifier):
        """Visita un identificatore (riferimento a variabile/funzione)"""
        self.set_node_info(node, scope=self.current_scope)

        try:
            # Risolve il riferimento
            symbol_info = self.current_scope.lookup(node.name)
            
            # Controlla se è una variabile locale non inizializzata
            if symbol_info.kind == SymbolKind.VARIABLE:
                is_uninitialized = self.get_node_info(symbol_info, 'uninitialized', False)
                if is_uninitialized:
                    # Questo è il caso di UnboundLocalError
                    raise UnboundLocalError(
                        f"cannot access local variable '{node.name}' "
                        f"where it is not associated with a value. "
                        f"Variable '{node.name}' is assigned in this scope, making it local, "
                        f"but it's referenced before assignment at {node.position}")
            
            self.set_node_info(node, resolved_info=symbol_info)
            print(
                f"  Risolto: {node.name} -> {symbol_info.unique_name} ({symbol_info.kind.value})")
        except ValueError:
            raise ValueError(
                f"Identificatore non dichiarato: {node.name} alla {node.position}")

    def visit_integer_literal(self, node: IntegerLiteral):
        """Visita un letterale intero"""
        self.set_node_info(node, scope=self.current_scope)

    def visit_boolean_literal(self, node: BooleanLiteral):
        """Visita un letterale booleano"""
        self.set_node_info(node, scope=self.current_scope)

    def visit_empty_list(self, node: EmptyList):
        """Visita una lista vuota"""
        self.set_node_info(node, scope=self.current_scope)

    def visit_binary_condition(self, node: BinaryCondition):
        """Visita una condizione binaria"""
        self.set_node_info(node, scope=self.current_scope)
        node.left.accept(self)
        node.right.accept(self)

    def visit_unary_condition(self, node: UnaryCondition):
        """Visita una condizione unaria"""
        self.set_node_info(node, scope=self.current_scope)
        node.operand.accept(self)

    def visit_comparison_condition(self, node: ComparisonCondition):
        """Visita una condizione di confronto"""
        self.set_node_info(node, scope=self.current_scope)
        node.left.accept(self)
        node.right.accept(self)

    # ==================== UTILITY METHODS ====================

    def print_symbol_tables(self):
        """Stampa tutte le symbol table per debug"""
        print("\n=== SYMBOL TABLES (GERARCHIA COMPLETA) ===")
        self._print_scope_recursive(self.global_scope, 0)
        print("\n=== RIEPILOGO VARIABILI PER SCOPE ===")
        self._print_variables_by_scope()

    def _print_scope_recursive(self, scope: SymbolTable, indent: int):
        """Stampa ricorsivamente uno scope e tutti i suoi figli"""
        prefix = "  " * indent

        # Stampa l'header dello scope
        symbol_count = len(scope.symbol2info)
        print(
            f"{prefix}📁 {scope.scope_name} (level {scope.level}) - {symbol_count} simboli")

        # Stampa tutti i simboli in questo scope
        if scope.symbol2info:
            for name, info in scope.symbol2info.items():
                icon = self._get_symbol_icon(info.kind)
                print(
                    f"{prefix}  {icon} {name} -> {info.unique_name} ({info.kind.value})")
        else:
            print(f"{prefix}  (vuoto)")

        # Stampa ricorsivamente tutti i figli
        if hasattr(scope, 'children') and scope.children:
            for child_scope in scope.children:
                self._print_scope_recursive(child_scope, indent + 1)

    def _get_symbol_icon(self, kind: SymbolKind) -> str:
        """Restituisce un'icona per il tipo di simbolo"""
        icons = {
            SymbolKind.VARIABLE: "🔤",
            SymbolKind.FUNCTION: "⚡",
            SymbolKind.PARAMETER: "📥"
        }
        return icons.get(kind, "❓")

    def _print_variables_by_scope(self):
        """Stampa tutte le variabili raggruppate per scope"""
        all_scopes = self._collect_all_scopes(self.global_scope)

        for scope in all_scopes:
            variables = [info for info in scope.symbol2info.values()
                         if info.kind == SymbolKind.VARIABLE]

            if variables:
                print(
                    f"\n🔤 Variabili in {scope.scope_name} (level {scope.level}):")
                for var_info in variables:
                    # Trova il nome originale della variabile
                    original_name = None
                    for name, info in scope.symbol2info.items():
                        if info == var_info:
                            original_name = name
                            break

                    print(f"   {original_name} -> {var_info.unique_name}")

    def _collect_all_scopes(self, scope: SymbolTable) -> List[SymbolTable]:
        """Raccoglie tutti i scope in una lista piatta"""
        scopes = [scope]
        if hasattr(scope, 'children') and scope.children:
            for child in scope.children:
                scopes.extend(self._collect_all_scopes(child))
        return scopes

    def print_decorated_ast(self):
        """Stampa l'AST decorato con le informazioni semantiche"""
        print("\n=== AST DECORATO CON INFORMAZIONI SEMANTICHE ===")
        self._print_decorated_node(self.global_scope, 0, is_root=True)

    def _print_decorated_node(self, scope: SymbolTable, indent: int, is_root: bool = False):
        """Stampa ricorsivamente l'AST decorato con scope e variabili"""
        prefix = "  " * indent

        if is_root:
            print(f"{prefix}🌐 GLOBAL SCOPE (level {scope.level})")
        else:
            print(f"{prefix}📦 {scope.scope_name.upper()} SCOPE (level {scope.level})")

        # Stampa simboli dichiarati in questo scope
        if scope.symbol2info:
            print(f"{prefix}├─ Simboli dichiarati:")
            for name, info in scope.symbol2info.items():
                icon = self._get_symbol_icon(info.kind)
                print(f"{prefix}│  {icon} {name} → {info.unique_name}")

        # Stampa informazioni sui nodi decorati in questo scope
        scope_nodes = self._get_nodes_in_scope(scope)
        if scope_nodes:
            print(f"{prefix}├─ Nodi AST decorati:")
            for node_type, nodes in scope_nodes.items():
                print(f"{prefix}│  📄 {node_type}: {len(nodes)} nodi")
                for node_info in nodes[:3]:  # Mostra solo i primi 3 per brevità
                    if 'variable_info' in node_info:
                        var_info = node_info['variable_info']
                        print(f"{prefix}│     → Assegnamento: {var_info.name} → {var_info.unique_name}")
                    elif 'resolved_info' in node_info:
                        res_info = node_info['resolved_info']
                        print(f"{prefix}│     → Riferimento: {res_info.name} → {res_info.unique_name}")
                if len(nodes) > 3:
                    print(f"{prefix}│     → ... e altri {len(nodes) - 3} nodi")

        # Stampa ricorsivamente i figli
        if hasattr(scope, 'children') and scope.children:
            print(f"{prefix}└─ Scope figli:")
            for i, child_scope in enumerate(scope.children):
                is_last = i == len(scope.children) - 1
                child_prefix = "└─" if is_last else "├─"
                print(f"{prefix}   {child_prefix}")
                self._print_decorated_node(child_scope, indent + 2)

    def _get_nodes_in_scope(self, scope: SymbolTable) -> dict:
        """Raggruppa i nodi decorati per tipo nello scope specificato"""
        nodes_by_type = {}

        for node_info_dict in self.node_info.values():
            if node_info_dict.get('scope') == scope:
                # Determina il tipo di nodo basandosi sulle informazioni disponibili
                node_type = "Unknown"
                if 'variable_info' in node_info_dict:
                    node_type = "Assignment"
                elif 'resolved_info' in node_info_dict:
                    resolved = node_info_dict['resolved_info']
                    if resolved.kind == SymbolKind.FUNCTION:
                        node_type = "FunctionCall"
                    elif resolved.kind == SymbolKind.VARIABLE:
                        node_type = "VariableReference"
                    elif resolved.kind == SymbolKind.PARAMETER:
                        node_type = "ParameterReference"
                elif 'symbol_info' in node_info_dict:
                    node_type = "FunctionDeclaration"
                else:
                    node_type = "Expression"

                if node_type not in nodes_by_type:
                    nodes_by_type[node_type] = []
                nodes_by_type[node_type].append(node_info_dict)

        return nodes_by_type
