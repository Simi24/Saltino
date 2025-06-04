# Generated from Saltino.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .SaltinoParser import SaltinoParser
else:
    from SaltinoParser import SaltinoParser

# This class defines a complete listener for a parse tree produced by SaltinoParser.
class SaltinoListener(ParseTreeListener):

    # Enter a parse tree produced by SaltinoParser#programma.
    def enterProgramma(self, ctx:SaltinoParser.ProgrammaContext):
        pass

    # Exit a parse tree produced by SaltinoParser#programma.
    def exitProgramma(self, ctx:SaltinoParser.ProgrammaContext):
        pass


    # Enter a parse tree produced by SaltinoParser#funzione.
    def enterFunzione(self, ctx:SaltinoParser.FunzioneContext):
        pass

    # Exit a parse tree produced by SaltinoParser#funzione.
    def exitFunzione(self, ctx:SaltinoParser.FunzioneContext):
        pass


    # Enter a parse tree produced by SaltinoParser#parametri.
    def enterParametri(self, ctx:SaltinoParser.ParametriContext):
        pass

    # Exit a parse tree produced by SaltinoParser#parametri.
    def exitParametri(self, ctx:SaltinoParser.ParametriContext):
        pass


    # Enter a parse tree produced by SaltinoParser#blocco.
    def enterBlocco(self, ctx:SaltinoParser.BloccoContext):
        pass

    # Exit a parse tree produced by SaltinoParser#blocco.
    def exitBlocco(self, ctx:SaltinoParser.BloccoContext):
        pass


    # Enter a parse tree produced by SaltinoParser#istruzione.
    def enterIstruzione(self, ctx:SaltinoParser.IstruzioneContext):
        pass

    # Exit a parse tree produced by SaltinoParser#istruzione.
    def exitIstruzione(self, ctx:SaltinoParser.IstruzioneContext):
        pass


    # Enter a parse tree produced by SaltinoParser#assegnamento.
    def enterAssegnamento(self, ctx:SaltinoParser.AssegnamentoContext):
        pass

    # Exit a parse tree produced by SaltinoParser#assegnamento.
    def exitAssegnamento(self, ctx:SaltinoParser.AssegnamentoContext):
        pass


    # Enter a parse tree produced by SaltinoParser#if_stmt.
    def enterIf_stmt(self, ctx:SaltinoParser.If_stmtContext):
        pass

    # Exit a parse tree produced by SaltinoParser#if_stmt.
    def exitIf_stmt(self, ctx:SaltinoParser.If_stmtContext):
        pass


    # Enter a parse tree produced by SaltinoParser#return_stmt.
    def enterReturn_stmt(self, ctx:SaltinoParser.Return_stmtContext):
        pass

    # Exit a parse tree produced by SaltinoParser#return_stmt.
    def exitReturn_stmt(self, ctx:SaltinoParser.Return_stmtContext):
        pass


    # Enter a parse tree produced by SaltinoParser#unario.
    def enterUnario(self, ctx:SaltinoParser.UnarioContext):
        pass

    # Exit a parse tree produced by SaltinoParser#unario.
    def exitUnario(self, ctx:SaltinoParser.UnarioContext):
        pass


    # Enter a parse tree produced by SaltinoParser#intero.
    def enterIntero(self, ctx:SaltinoParser.InteroContext):
        pass

    # Exit a parse tree produced by SaltinoParser#intero.
    def exitIntero(self, ctx:SaltinoParser.InteroContext):
        pass


    # Enter a parse tree produced by SaltinoParser#potenza.
    def enterPotenza(self, ctx:SaltinoParser.PotenzaContext):
        pass

    # Exit a parse tree produced by SaltinoParser#potenza.
    def exitPotenza(self, ctx:SaltinoParser.PotenzaContext):
        pass


    # Enter a parse tree produced by SaltinoParser#chiamataFunzione.
    def enterChiamataFunzione(self, ctx:SaltinoParser.ChiamataFunzioneContext):
        pass

    # Exit a parse tree produced by SaltinoParser#chiamataFunzione.
    def exitChiamataFunzione(self, ctx:SaltinoParser.ChiamataFunzioneContext):
        pass


    # Enter a parse tree produced by SaltinoParser#identificatore.
    def enterIdentificatore(self, ctx:SaltinoParser.IdentificatoreContext):
        pass

    # Exit a parse tree produced by SaltinoParser#identificatore.
    def exitIdentificatore(self, ctx:SaltinoParser.IdentificatoreContext):
        pass


    # Enter a parse tree produced by SaltinoParser#parantesi.
    def enterParantesi(self, ctx:SaltinoParser.ParantesiContext):
        pass

    # Exit a parse tree produced by SaltinoParser#parantesi.
    def exitParantesi(self, ctx:SaltinoParser.ParantesiContext):
        pass


    # Enter a parse tree produced by SaltinoParser#moltiplicazione.
    def enterMoltiplicazione(self, ctx:SaltinoParser.MoltiplicazioneContext):
        pass

    # Exit a parse tree produced by SaltinoParser#moltiplicazione.
    def exitMoltiplicazione(self, ctx:SaltinoParser.MoltiplicazioneContext):
        pass


    # Enter a parse tree produced by SaltinoParser#addizione.
    def enterAddizione(self, ctx:SaltinoParser.AddizioneContext):
        pass

    # Exit a parse tree produced by SaltinoParser#addizione.
    def exitAddizione(self, ctx:SaltinoParser.AddizioneContext):
        pass


    # Enter a parse tree produced by SaltinoParser#listaVuota.
    def enterListaVuota(self, ctx:SaltinoParser.ListaVuotaContext):
        pass

    # Exit a parse tree produced by SaltinoParser#listaVuota.
    def exitListaVuota(self, ctx:SaltinoParser.ListaVuotaContext):
        pass


    # Enter a parse tree produced by SaltinoParser#headTail.
    def enterHeadTail(self, ctx:SaltinoParser.HeadTailContext):
        pass

    # Exit a parse tree produced by SaltinoParser#headTail.
    def exitHeadTail(self, ctx:SaltinoParser.HeadTailContext):
        pass


    # Enter a parse tree produced by SaltinoParser#booleanoLiterale.
    def enterBooleanoLiterale(self, ctx:SaltinoParser.BooleanoLiteraleContext):
        pass

    # Exit a parse tree produced by SaltinoParser#booleanoLiterale.
    def exitBooleanoLiterale(self, ctx:SaltinoParser.BooleanoLiteraleContext):
        pass


    # Enter a parse tree produced by SaltinoParser#cons.
    def enterCons(self, ctx:SaltinoParser.ConsContext):
        pass

    # Exit a parse tree produced by SaltinoParser#cons.
    def exitCons(self, ctx:SaltinoParser.ConsContext):
        pass


    # Enter a parse tree produced by SaltinoParser#argomenti.
    def enterArgomenti(self, ctx:SaltinoParser.ArgomentiContext):
        pass

    # Exit a parse tree produced by SaltinoParser#argomenti.
    def exitArgomenti(self, ctx:SaltinoParser.ArgomentiContext):
        pass


    # Enter a parse tree produced by SaltinoParser#condizione.
    def enterCondizione(self, ctx:SaltinoParser.CondizioneContext):
        pass

    # Exit a parse tree produced by SaltinoParser#condizione.
    def exitCondizione(self, ctx:SaltinoParser.CondizioneContext):
        pass


    # Enter a parse tree produced by SaltinoParser#condOr.
    def enterCondOr(self, ctx:SaltinoParser.CondOrContext):
        pass

    # Exit a parse tree produced by SaltinoParser#condOr.
    def exitCondOr(self, ctx:SaltinoParser.CondOrContext):
        pass


    # Enter a parse tree produced by SaltinoParser#condAnd.
    def enterCondAnd(self, ctx:SaltinoParser.CondAndContext):
        pass

    # Exit a parse tree produced by SaltinoParser#condAnd.
    def exitCondAnd(self, ctx:SaltinoParser.CondAndContext):
        pass


    # Enter a parse tree produced by SaltinoParser#condNot.
    def enterCondNot(self, ctx:SaltinoParser.CondNotContext):
        pass

    # Exit a parse tree produced by SaltinoParser#condNot.
    def exitCondNot(self, ctx:SaltinoParser.CondNotContext):
        pass


    # Enter a parse tree produced by SaltinoParser#condAtom.
    def enterCondAtom(self, ctx:SaltinoParser.CondAtomContext):
        pass

    # Exit a parse tree produced by SaltinoParser#condAtom.
    def exitCondAtom(self, ctx:SaltinoParser.CondAtomContext):
        pass


    # Enter a parse tree produced by SaltinoParser#relop.
    def enterRelop(self, ctx:SaltinoParser.RelopContext):
        pass

    # Exit a parse tree produced by SaltinoParser#relop.
    def exitRelop(self, ctx:SaltinoParser.RelopContext):
        pass



del SaltinoParser