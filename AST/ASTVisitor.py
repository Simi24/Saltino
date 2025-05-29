"""
ASTVisitor per il linguaggio Saltino.

Questo visitor trasforma il parse tree generato da ANTLR in un AST
utilizzando le classi definite in ASTNodes.py.
"""

from Grammatica.SaltinoParser import SaltinoParser
from Grammatica.SaltinoVisitor import SaltinoVisitor
from .ASTNodes import *
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# TODO: Add type checking for the visitor methods
# TODO: Add error handling
# TODO: Add scope management for variables and functions

class SaltinoASTVisitor(SaltinoVisitor):
    """
    Visitor che trasforma il parse tree di ANTLR in un AST.

    Ogni metodo visit_* corrisponde a una regola della grammatica
    e restituisce il nodo AST appropriato.
    """

    def __init__(self):
        super().__init__()

    def _get_position(self, ctx):
        """Estrae la posizione dal contesto del parser."""
        if ctx.start:
            return SourcePosition(ctx.start.line, ctx.start.column)
        return None

    # ==================== PROGRAMMA E FUNZIONI ====================

    def visitProgramma(self, ctx: SaltinoParser.ProgrammaContext):
        """Visita il programma principale."""
        functions = []
        for func_ctx in ctx.funzione():
            # print(f"Visiting function: {func_ctx.getText()}")
            functions.append(self.visitFunzione(func_ctx))
        return Program(functions, self._get_position(ctx))

    def visitFunzione(self, ctx: SaltinoParser.FunzioneContext):
        """Visita una definizione di funzione."""
        name = ctx.ID().getText()
        # print(f"Visiting function definition: {name}")

        # Parametri (opzionali)
        parameters = []
        if ctx.parametri():
            parameters = self.visit(ctx.parametri())

        # Corpo della funzione
        body = self.visit(ctx.blocco())

        return Function(name, parameters, body, self._get_position(ctx))

    def visitParametri(self, ctx: SaltinoParser.ParametriContext):
        """Visita la lista dei parametri."""
        parameters = []
        for id_node in ctx.ID():
            parameters.append(id_node.getText())
        return parameters

    # ==================== BLOCCHI E ISTRUZIONI ====================

    def visitBlocco(self, ctx: SaltinoParser.BloccoContext):
        """Visita un blocco di istruzioni."""
        statements = []

        # Un blocco può contenere istruzioni e blocchi annidati
        for child in ctx.children:
            if hasattr(child, 'getRuleIndex'):  # È un nodo grammaticale, non un token
                visited = self.visit(child)
                if visited is not None:
                    statements.append(visited)

        return Block(statements, self._get_position(ctx))

    def visitIstruzione(self, ctx: SaltinoParser.IstruzioneContext):
        """Visita un'istruzione generica."""
        # Determina il tipo di istruzione e visita il sottotipo appropriato
        if ctx.assegnamento():
            return self.visit(ctx.assegnamento())
        elif ctx.if_stmt():
            return self.visit(ctx.if_stmt())
        elif ctx.return_stmt():
            return self.visit(ctx.return_stmt())
        else:
            return None

    def visitAssegnamento(self, ctx: SaltinoParser.AssegnamentoContext):
        """Visita un assegnamento."""
        variable = ctx.ID().getText()

        # Il valore può essere un'espressione o una condizione
        if ctx.espressione():
            value = self.visit(ctx.espressione())
        elif ctx.condizione():
            value = self.visit(ctx.condizione())
        else:
            value = None

        return Assignment(variable, value, self._get_position(ctx))

    def visitIf_stmt(self, ctx: SaltinoParser.If_stmtContext):
        """Visita un'istruzione if-then-else."""
        condition = self.visit(ctx.condizione())
        then_block = self.visit(ctx.blocco(0))  # Primo blocco

        # else è opzionale
        else_block = None
        if len(ctx.blocco()) > 1:
            else_block = self.visit(ctx.blocco(1))

        return IfStatement(condition, then_block, else_block, self._get_position(ctx))

    def visitReturn_stmt(self, ctx: SaltinoParser.Return_stmtContext):
        """Visita un'istruzione return."""
        # Il valore può essere un'espressione o una condizione
        if ctx.espressione():
            value = self.visit(ctx.espressione())
        elif ctx.condizione():
            value = self.visit(ctx.condizione())
        else:
            value = None

        return ReturnStatement(value, self._get_position(ctx))

    # ==================== ESPRESSIONI ====================

    def visitAddizione(self, ctx: SaltinoParser.AddizioneContext):
        """Visita addizione o sottrazione."""
        left = self.visit(ctx.espressione(0))
        right = self.visit(ctx.espressione(1))

        # Determina l'operatore dal testo
        op_text = ctx.getChild(1).getText()
        return BinaryExpression(left, op_text, right, self._get_position(ctx))

    def visitMoltiplicazione(self, ctx: SaltinoParser.MoltiplicazioneContext):
        """Visita moltiplicazione, divisione o modulo."""
        left = self.visit(ctx.espressione(0))
        right = self.visit(ctx.espressione(1))

        op_text = ctx.getChild(1).getText()
        return BinaryExpression(left, op_text, right, self._get_position(ctx))

    def visitPotenza(self, ctx: SaltinoParser.PotenzaContext):
        """Visita potenza."""
        left = self.visit(ctx.espressione(0))
        right = self.visit(ctx.espressione(1))

        return BinaryExpression(left, '^', right, self._get_position(ctx))

    def visitCons(self, ctx: SaltinoParser.ConsContext):
        """Visita operatore cons (::)."""
        left = self.visit(ctx.espressione(0))
        right = self.visit(ctx.espressione(1))

        return BinaryExpression(left, '::', right, self._get_position(ctx))

    def visitUnario(self, ctx: SaltinoParser.UnarioContext):
        """Visita espressione unaria (+ o -)."""
        operand = self.visit(ctx.espressione())
        op_text = ctx.getChild(0).getText()

        return UnaryExpression(op_text, operand, self._get_position(ctx))

    def visitHeadTail(self, ctx: SaltinoParser.HeadTailContext):
        """Visita operatori head e tail."""
        operand = self.visit(ctx.espressione())
        op_text = ctx.getChild(0).getText()  # 'head' o 'tail'

        return UnaryExpression(op_text, operand, self._get_position(ctx))

    def visitChiamataFunzione(self, ctx: SaltinoParser.ChiamataFunzioneContext):
        """Visita chiamata di funzione."""
        function = self.visit(ctx.espressione())

        # Argomenti (opzionali)
        arguments = []
        if ctx.argomenti():
            arguments = self.visit(ctx.argomenti())

        return FunctionCall(function, arguments, self._get_position(ctx))

    def visitArgomenti(self, ctx: SaltinoParser.ArgomentiContext):
        """Visita lista di argomenti."""
        arguments = []

        # Gli argomenti possono essere espressioni o condizioni
        for i in range(len(ctx.children)):
            child = ctx.children[i]
            if hasattr(child, 'getRuleIndex'):  # È un nodo grammaticale
                visited = self.visit(child)
                if visited is not None:
                    arguments.append(visited)

        return arguments

    def visitIntero(self, ctx: SaltinoParser.InteroContext):
        """Visita letterale intero."""
        value = int(ctx.INT().getText())
        return IntegerLiteral(value, self._get_position(ctx))

    def visitBooleanoLiterale(self, ctx: SaltinoParser.BooleanoLiteraleContext):
        """Visita letterale booleano nelle espressioni."""
        value = ctx.getText() == 'true'
        return BooleanLiteral(value, self._get_position(ctx))

    def visitIdentificatore(self, ctx: SaltinoParser.IdentificatoreContext):
        """Visita identificatore."""
        name = ctx.ID().getText()
        return Identifier(name, self._get_position(ctx))

    def visitListaVuota(self, ctx: SaltinoParser.ListaVuotaContext):
        """Visita lista vuota []."""
        return EmptyList(self._get_position(ctx))

    def visitParantesi(self, ctx: SaltinoParser.ParantesiContext):
        """Visita espressione tra parentesi."""
        # Le parentesi non creano un nodo specifico, restituiamo solo l'espressione interna
        return self.visit(ctx.espressione())

    # ==================== CONDIZIONI ====================

    def visitCondizione(self, ctx: SaltinoParser.CondizioneContext):
        """Visita il punto di ingresso per le condizioni."""
        return self.visit(ctx.condOr())

    def visitCondOr(self, ctx: SaltinoParser.CondOrContext):
        """Visita operatore logico OR (precedenza più bassa)."""
        # condOr: condAnd ('or' condAnd)*
        result = self.visit(ctx.condAnd(0))  # Primo operando
        
        # Se ci sono più operandi, costruisci una catena di OR associativi a sinistra
        for i in range(1, len(ctx.condAnd())):
            right = self.visit(ctx.condAnd(i))
            result = BinaryCondition(result, 'or', right, self._get_position(ctx))
        
        return result

    def visitCondAnd(self, ctx: SaltinoParser.CondAndContext):
        """Visita operatore logico AND."""
        # condAnd: condNot ('and' condNot)*
        result = self.visit(ctx.condNot(0))  # Primo operando
        
        # Se ci sono più operandi, costruisci una catena di AND associativi a sinistra
        for i in range(1, len(ctx.condNot())):
            right = self.visit(ctx.condNot(i))
            result = BinaryCondition(result, 'and', right, self._get_position(ctx))
        
        return result

    def visitCondNot(self, ctx: SaltinoParser.CondNotContext):
        """Visita negazione logica NOT."""
        # condNot: '!' condNot | condAtom
        if ctx.getText().startswith('!'):
            # È una negazione
            operand = self.visit(ctx.condNot())
            return UnaryCondition('!', operand, self._get_position(ctx))
        else:
            # È un atomo
            return self.visit(ctx.condAtom())

    def visitCondAtom(self, ctx: SaltinoParser.CondAtomContext):
        """Visita condizioni atomiche (precedenza più alta)."""
        # condAtom: espressione relop espressione | 'true' | 'false' | ID | '(' condizione ')'
        
        if ctx.relop():
            # È un confronto: espressione relop espressione
            left = self.visit(ctx.espressione(0))
            right = self.visit(ctx.espressione(1))
            op_text = self.visit(ctx.relop())
            return ComparisonCondition(left, op_text, right, self._get_position(ctx))
        
        elif ctx.getText() == 'true':
            return BooleanLiteral(True, self._get_position(ctx))
        
        elif ctx.getText() == 'false':
            return BooleanLiteral(False, self._get_position(ctx))
        
        elif ctx.ID():
            # Variabile booleana
            name = ctx.ID().getText()
            return Identifier(name, self._get_position(ctx))
        
        elif ctx.condizione():
            # Parentesi: '(' condizione ')'
            return self.visit(ctx.condizione())
        
        else:
            raise ValueError(f"Tipo di condizione atomica non riconosciuto: {ctx.getText()}")

    def visitRelop(self, ctx: SaltinoParser.RelopContext):
        """Visita operatori di confronto."""
        # relop: '<=' | '<' | '==' | '>' | '>='
        return ctx.getText()


# ==================== UTILITY FUNCTIONS ====================

def build_ast(parse_tree) -> Program:
    """
    Costruisce un AST a partire dal parse tree di ANTLR.

    Args:
        parse_tree: Il parse tree generato dal parser ANTLR

    Returns:
        Program: Il nodo radice dell'AST
    """
    visitor = SaltinoASTVisitor()
    return visitor.visit(parse_tree)


def print_ast(node: ASTNode, indent: int = 0) -> str:
    """
    Stampa una rappresentazione testuale dell'AST.

    Args:
        node: Il nodo da stampare
        indent: Livello di indentazione

    Returns:
        str: Rappresentazione testuale dell'AST
    """
    result = "  " * indent + str(node) + "\n"

    # Attraversa ricorsivamente i figli
    if hasattr(node, 'functions'):
        for func in node.functions:
            result += print_ast(func, indent + 1)

    elif hasattr(node, 'body'):
        result += print_ast(node.body, indent + 1)

    elif hasattr(node, 'statements'):
        for stmt in node.statements:
            result += print_ast(stmt, indent + 1)

    elif hasattr(node, 'value') and hasattr(node, 'variable'):
        result += print_ast(node.value, indent + 1)

    elif hasattr(node, 'condition') and hasattr(node, 'then_block'):
        result += print_ast(node.condition, indent + 1)
        result += print_ast(node.then_block, indent + 1)
        if node.else_block:
            result += print_ast(node.else_block, indent + 1)

    elif hasattr(node, 'value') and not hasattr(node, 'variable'):
        result += print_ast(node.value, indent + 1)

    elif hasattr(node, 'left') and hasattr(node, 'right'):
        result += print_ast(node.left, indent + 1)
        result += print_ast(node.right, indent + 1)

    elif hasattr(node, 'operand'):
        result += print_ast(node.operand, indent + 1)

    elif hasattr(node, 'function') and hasattr(node, 'arguments'):
        result += print_ast(node.function, indent + 1)
        for arg in node.arguments:
            result += print_ast(arg, indent + 1)

    return result
