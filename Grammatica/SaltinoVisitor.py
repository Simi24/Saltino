# Generated from Saltino.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .SaltinoParser import SaltinoParser
else:
    from SaltinoParser import SaltinoParser

# This class defines a complete generic visitor for a parse tree produced by SaltinoParser.

class SaltinoVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by SaltinoParser#programma.
    def visitProgramma(self, ctx:SaltinoParser.ProgrammaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#funzione.
    def visitFunzione(self, ctx:SaltinoParser.FunzioneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#parametri.
    def visitParametri(self, ctx:SaltinoParser.ParametriContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#blocco.
    def visitBlocco(self, ctx:SaltinoParser.BloccoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#istruzione.
    def visitIstruzione(self, ctx:SaltinoParser.IstruzioneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#assegnamento.
    def visitAssegnamento(self, ctx:SaltinoParser.AssegnamentoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#if_stmt.
    def visitIf_stmt(self, ctx:SaltinoParser.If_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#return_stmt.
    def visitReturn_stmt(self, ctx:SaltinoParser.Return_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#unario.
    def visitUnario(self, ctx:SaltinoParser.UnarioContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#intero.
    def visitIntero(self, ctx:SaltinoParser.InteroContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#potenza.
    def visitPotenza(self, ctx:SaltinoParser.PotenzaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#chiamataFunzione.
    def visitChiamataFunzione(self, ctx:SaltinoParser.ChiamataFunzioneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#identificatore.
    def visitIdentificatore(self, ctx:SaltinoParser.IdentificatoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#parantesi.
    def visitParantesi(self, ctx:SaltinoParser.ParantesiContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#moltiplicazione.
    def visitMoltiplicazione(self, ctx:SaltinoParser.MoltiplicazioneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#addizione.
    def visitAddizione(self, ctx:SaltinoParser.AddizioneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#listaVuota.
    def visitListaVuota(self, ctx:SaltinoParser.ListaVuotaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#headTail.
    def visitHeadTail(self, ctx:SaltinoParser.HeadTailContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#booleanoLiterale.
    def visitBooleanoLiterale(self, ctx:SaltinoParser.BooleanoLiteraleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#cons.
    def visitCons(self, ctx:SaltinoParser.ConsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#argomenti.
    def visitArgomenti(self, ctx:SaltinoParser.ArgomentiContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#parentesiCondizione.
    def visitParentesiCondizione(self, ctx:SaltinoParser.ParentesiCondizioneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#variabileBooleana.
    def visitVariabileBooleana(self, ctx:SaltinoParser.VariabileBooleanaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#booleano.
    def visitBooleano(self, ctx:SaltinoParser.BooleanoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#logico.
    def visitLogico(self, ctx:SaltinoParser.LogicoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#confronto.
    def visitConfronto(self, ctx:SaltinoParser.ConfrontoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#negazione.
    def visitNegazione(self, ctx:SaltinoParser.NegazioneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaltinoParser#espressioneCondizione.
    def visitEspressioneCondizione(self, ctx:SaltinoParser.EspressioneCondizioneContext):
        return self.visitChildren(ctx)



del SaltinoParser