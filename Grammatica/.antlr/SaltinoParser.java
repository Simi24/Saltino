// Generated from /home/simiarch/projects/Saltino/Grammatica/Saltino.g4 by ANTLR 4.13.1
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast", "CheckReturnValue"})
public class SaltinoParser extends Parser {
	static { RuntimeMetaData.checkVersion("4.13.1", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		T__0=1, T__1=2, T__2=3, T__3=4, T__4=5, T__5=6, T__6=7, T__7=8, T__8=9, 
		T__9=10, T__10=11, T__11=12, T__12=13, T__13=14, T__14=15, T__15=16, T__16=17, 
		T__17=18, T__18=19, T__19=20, T__20=21, T__21=22, T__22=23, T__23=24, 
		T__24=25, T__25=26, T__26=27, T__27=28, T__28=29, T__29=30, ID=31, INT=32, 
		WS=33, COMMENT=34, BLOCK_COMMENT=35;
	public static final int
		RULE_programma = 0, RULE_funzione = 1, RULE_parametri = 2, RULE_blocco = 3, 
		RULE_istruzione = 4, RULE_assegnamento = 5, RULE_if_stmt = 6, RULE_return_stmt = 7, 
		RULE_espressione = 8, RULE_argomenti = 9, RULE_condizione = 10;
	private static String[] makeRuleNames() {
		return new String[] {
			"programma", "funzione", "parametri", "blocco", "istruzione", "assegnamento", 
			"if_stmt", "return_stmt", "espressione", "argomenti", "condizione"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'def'", "'('", "')'", "','", "'{'", "'}'", "'='", "'if'", "'else'", 
			"'return'", "'head'", "'tail'", "'^'", "'+'", "'-'", "'*'", "'/'", "'%'", 
			"'::'", "'[]'", "'and'", "'or'", "'!'", "'<='", "'<'", "'=='", "'>'", 
			"'>='", "'true'", "'false'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, "ID", "INT", "WS", "COMMENT", 
			"BLOCK_COMMENT"
		};
	}
	private static final String[] _SYMBOLIC_NAMES = makeSymbolicNames();
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}

	@Override
	public String getGrammarFileName() { return "Saltino.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public SaltinoParser(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ProgrammaContext extends ParserRuleContext {
		public TerminalNode EOF() { return getToken(SaltinoParser.EOF, 0); }
		public List<FunzioneContext> funzione() {
			return getRuleContexts(FunzioneContext.class);
		}
		public FunzioneContext funzione(int i) {
			return getRuleContext(FunzioneContext.class,i);
		}
		public ProgrammaContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_programma; }
	}

	public final ProgrammaContext programma() throws RecognitionException {
		ProgrammaContext _localctx = new ProgrammaContext(_ctx, getState());
		enterRule(_localctx, 0, RULE_programma);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(23); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(22);
				funzione();
				}
				}
				setState(25); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( _la==T__0 );
			setState(27);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class FunzioneContext extends ParserRuleContext {
		public TerminalNode ID() { return getToken(SaltinoParser.ID, 0); }
		public BloccoContext blocco() {
			return getRuleContext(BloccoContext.class,0);
		}
		public ParametriContext parametri() {
			return getRuleContext(ParametriContext.class,0);
		}
		public FunzioneContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_funzione; }
	}

	public final FunzioneContext funzione() throws RecognitionException {
		FunzioneContext _localctx = new FunzioneContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_funzione);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(29);
			match(T__0);
			setState(30);
			match(ID);
			setState(31);
			match(T__1);
			setState(33);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ID) {
				{
				setState(32);
				parametri();
				}
			}

			setState(35);
			match(T__2);
			setState(36);
			blocco();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ParametriContext extends ParserRuleContext {
		public List<TerminalNode> ID() { return getTokens(SaltinoParser.ID); }
		public TerminalNode ID(int i) {
			return getToken(SaltinoParser.ID, i);
		}
		public ParametriContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_parametri; }
	}

	public final ParametriContext parametri() throws RecognitionException {
		ParametriContext _localctx = new ParametriContext(_ctx, getState());
		enterRule(_localctx, 4, RULE_parametri);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(38);
			match(ID);
			setState(43);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==T__3) {
				{
				{
				setState(39);
				match(T__3);
				setState(40);
				match(ID);
				}
				}
				setState(45);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class BloccoContext extends ParserRuleContext {
		public List<IstruzioneContext> istruzione() {
			return getRuleContexts(IstruzioneContext.class);
		}
		public IstruzioneContext istruzione(int i) {
			return getRuleContext(IstruzioneContext.class,i);
		}
		public List<BloccoContext> blocco() {
			return getRuleContexts(BloccoContext.class);
		}
		public BloccoContext blocco(int i) {
			return getRuleContext(BloccoContext.class,i);
		}
		public BloccoContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_blocco; }
	}

	public final BloccoContext blocco() throws RecognitionException {
		BloccoContext _localctx = new BloccoContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_blocco);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(46);
			match(T__4);
			setState(51);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 2147484960L) != 0)) {
				{
				setState(49);
				_errHandler.sync(this);
				switch (_input.LA(1)) {
				case T__7:
				case T__9:
				case ID:
					{
					setState(47);
					istruzione();
					}
					break;
				case T__4:
					{
					setState(48);
					blocco();
					}
					break;
				default:
					throw new NoViableAltException(this);
				}
				}
				setState(53);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(54);
			match(T__5);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class IstruzioneContext extends ParserRuleContext {
		public AssegnamentoContext assegnamento() {
			return getRuleContext(AssegnamentoContext.class,0);
		}
		public If_stmtContext if_stmt() {
			return getRuleContext(If_stmtContext.class,0);
		}
		public Return_stmtContext return_stmt() {
			return getRuleContext(Return_stmtContext.class,0);
		}
		public IstruzioneContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_istruzione; }
	}

	public final IstruzioneContext istruzione() throws RecognitionException {
		IstruzioneContext _localctx = new IstruzioneContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_istruzione);
		try {
			setState(59);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case ID:
				enterOuterAlt(_localctx, 1);
				{
				setState(56);
				assegnamento();
				}
				break;
			case T__7:
				enterOuterAlt(_localctx, 2);
				{
				setState(57);
				if_stmt();
				}
				break;
			case T__9:
				enterOuterAlt(_localctx, 3);
				{
				setState(58);
				return_stmt();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AssegnamentoContext extends ParserRuleContext {
		public TerminalNode ID() { return getToken(SaltinoParser.ID, 0); }
		public EspressioneContext espressione() {
			return getRuleContext(EspressioneContext.class,0);
		}
		public CondizioneContext condizione() {
			return getRuleContext(CondizioneContext.class,0);
		}
		public AssegnamentoContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_assegnamento; }
	}

	public final AssegnamentoContext assegnamento() throws RecognitionException {
		AssegnamentoContext _localctx = new AssegnamentoContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_assegnamento);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(61);
			match(ID);
			setState(62);
			match(T__6);
			setState(65);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,6,_ctx) ) {
			case 1:
				{
				setState(63);
				espressione(0);
				}
				break;
			case 2:
				{
				setState(64);
				condizione(0);
				}
				break;
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class If_stmtContext extends ParserRuleContext {
		public CondizioneContext condizione() {
			return getRuleContext(CondizioneContext.class,0);
		}
		public List<BloccoContext> blocco() {
			return getRuleContexts(BloccoContext.class);
		}
		public BloccoContext blocco(int i) {
			return getRuleContext(BloccoContext.class,i);
		}
		public If_stmtContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_if_stmt; }
	}

	public final If_stmtContext if_stmt() throws RecognitionException {
		If_stmtContext _localctx = new If_stmtContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_if_stmt);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(67);
			match(T__7);
			setState(68);
			match(T__1);
			setState(69);
			condizione(0);
			setState(70);
			match(T__2);
			setState(71);
			blocco();
			setState(74);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__8) {
				{
				setState(72);
				match(T__8);
				setState(73);
				blocco();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class Return_stmtContext extends ParserRuleContext {
		public EspressioneContext espressione() {
			return getRuleContext(EspressioneContext.class,0);
		}
		public CondizioneContext condizione() {
			return getRuleContext(CondizioneContext.class,0);
		}
		public Return_stmtContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_return_stmt; }
	}

	public final Return_stmtContext return_stmt() throws RecognitionException {
		Return_stmtContext _localctx = new Return_stmtContext(_ctx, getState());
		enterRule(_localctx, 14, RULE_return_stmt);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(76);
			match(T__9);
			setState(79);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,8,_ctx) ) {
			case 1:
				{
				setState(77);
				espressione(0);
				}
				break;
			case 2:
				{
				setState(78);
				condizione(0);
				}
				break;
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class EspressioneContext extends ParserRuleContext {
		public EspressioneContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_espressione; }
	 
		public EspressioneContext() { }
		public void copyFrom(EspressioneContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class UnarioContext extends EspressioneContext {
		public EspressioneContext espressione() {
			return getRuleContext(EspressioneContext.class,0);
		}
		public UnarioContext(EspressioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class InteroContext extends EspressioneContext {
		public TerminalNode INT() { return getToken(SaltinoParser.INT, 0); }
		public InteroContext(EspressioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class PotenzaContext extends EspressioneContext {
		public List<EspressioneContext> espressione() {
			return getRuleContexts(EspressioneContext.class);
		}
		public EspressioneContext espressione(int i) {
			return getRuleContext(EspressioneContext.class,i);
		}
		public PotenzaContext(EspressioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ChiamataFunzioneContext extends EspressioneContext {
		public EspressioneContext espressione() {
			return getRuleContext(EspressioneContext.class,0);
		}
		public ArgomentiContext argomenti() {
			return getRuleContext(ArgomentiContext.class,0);
		}
		public ChiamataFunzioneContext(EspressioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class IdentificatoreContext extends EspressioneContext {
		public TerminalNode ID() { return getToken(SaltinoParser.ID, 0); }
		public IdentificatoreContext(EspressioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ParantesiContext extends EspressioneContext {
		public EspressioneContext espressione() {
			return getRuleContext(EspressioneContext.class,0);
		}
		public ParantesiContext(EspressioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class MoltiplicazioneContext extends EspressioneContext {
		public List<EspressioneContext> espressione() {
			return getRuleContexts(EspressioneContext.class);
		}
		public EspressioneContext espressione(int i) {
			return getRuleContext(EspressioneContext.class,i);
		}
		public MoltiplicazioneContext(EspressioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class AddizioneContext extends EspressioneContext {
		public List<EspressioneContext> espressione() {
			return getRuleContexts(EspressioneContext.class);
		}
		public EspressioneContext espressione(int i) {
			return getRuleContext(EspressioneContext.class,i);
		}
		public AddizioneContext(EspressioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ListaVuotaContext extends EspressioneContext {
		public ListaVuotaContext(EspressioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class HeadTailContext extends EspressioneContext {
		public EspressioneContext espressione() {
			return getRuleContext(EspressioneContext.class,0);
		}
		public HeadTailContext(EspressioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ConsContext extends EspressioneContext {
		public List<EspressioneContext> espressione() {
			return getRuleContexts(EspressioneContext.class);
		}
		public EspressioneContext espressione(int i) {
			return getRuleContext(EspressioneContext.class,i);
		}
		public ConsContext(EspressioneContext ctx) { copyFrom(ctx); }
	}

	public final EspressioneContext espressione() throws RecognitionException {
		return espressione(0);
	}

	private EspressioneContext espressione(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		EspressioneContext _localctx = new EspressioneContext(_ctx, _parentState);
		EspressioneContext _prevctx = _localctx;
		int _startState = 16;
		enterRecursionRule(_localctx, 16, RULE_espressione, _p);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(96);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__10:
			case T__11:
				{
				_localctx = new HeadTailContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;

				setState(82);
				_la = _input.LA(1);
				if ( !(_la==T__10 || _la==T__11) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(83);
				match(T__1);
				setState(84);
				espressione(0);
				setState(85);
				match(T__2);
				}
				break;
			case T__13:
			case T__14:
				{
				_localctx = new UnarioContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(87);
				_la = _input.LA(1);
				if ( !(_la==T__13 || _la==T__14) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(88);
				espressione(8);
				}
				break;
			case T__19:
				{
				_localctx = new ListaVuotaContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(89);
				match(T__19);
				}
				break;
			case INT:
				{
				_localctx = new InteroContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(90);
				match(INT);
				}
				break;
			case ID:
				{
				_localctx = new IdentificatoreContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(91);
				match(ID);
				}
				break;
			case T__1:
				{
				_localctx = new ParantesiContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(92);
				match(T__1);
				setState(93);
				espressione(0);
				setState(94);
				match(T__2);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
			_ctx.stop = _input.LT(-1);
			setState(118);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,12,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					setState(116);
					_errHandler.sync(this);
					switch ( getInterpreter().adaptivePredict(_input,11,_ctx) ) {
					case 1:
						{
						_localctx = new PotenzaContext(new EspressioneContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_espressione);
						setState(98);
						if (!(precpred(_ctx, 9))) throw new FailedPredicateException(this, "precpred(_ctx, 9)");
						setState(99);
						match(T__12);
						setState(100);
						espressione(9);
						}
						break;
					case 2:
						{
						_localctx = new MoltiplicazioneContext(new EspressioneContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_espressione);
						setState(101);
						if (!(precpred(_ctx, 7))) throw new FailedPredicateException(this, "precpred(_ctx, 7)");
						setState(102);
						_la = _input.LA(1);
						if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 458752L) != 0)) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						setState(103);
						espressione(8);
						}
						break;
					case 3:
						{
						_localctx = new AddizioneContext(new EspressioneContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_espressione);
						setState(104);
						if (!(precpred(_ctx, 6))) throw new FailedPredicateException(this, "precpred(_ctx, 6)");
						setState(105);
						_la = _input.LA(1);
						if ( !(_la==T__13 || _la==T__14) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						setState(106);
						espressione(7);
						}
						break;
					case 4:
						{
						_localctx = new ConsContext(new EspressioneContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_espressione);
						setState(107);
						if (!(precpred(_ctx, 5))) throw new FailedPredicateException(this, "precpred(_ctx, 5)");
						setState(108);
						match(T__18);
						setState(109);
						espressione(5);
						}
						break;
					case 5:
						{
						_localctx = new ChiamataFunzioneContext(new EspressioneContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_espressione);
						setState(110);
						if (!(precpred(_ctx, 11))) throw new FailedPredicateException(this, "precpred(_ctx, 11)");
						setState(111);
						match(T__1);
						setState(113);
						_errHandler.sync(this);
						_la = _input.LA(1);
						if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 8062556164L) != 0)) {
							{
							setState(112);
							argomenti();
							}
						}

						setState(115);
						match(T__2);
						}
						break;
					}
					} 
				}
				setState(120);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,12,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ArgomentiContext extends ParserRuleContext {
		public List<EspressioneContext> espressione() {
			return getRuleContexts(EspressioneContext.class);
		}
		public EspressioneContext espressione(int i) {
			return getRuleContext(EspressioneContext.class,i);
		}
		public List<CondizioneContext> condizione() {
			return getRuleContexts(CondizioneContext.class);
		}
		public CondizioneContext condizione(int i) {
			return getRuleContext(CondizioneContext.class,i);
		}
		public ArgomentiContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_argomenti; }
	}

	public final ArgomentiContext argomenti() throws RecognitionException {
		ArgomentiContext _localctx = new ArgomentiContext(_ctx, getState());
		enterRule(_localctx, 18, RULE_argomenti);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(123);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,13,_ctx) ) {
			case 1:
				{
				setState(121);
				espressione(0);
				}
				break;
			case 2:
				{
				setState(122);
				condizione(0);
				}
				break;
			}
			setState(132);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==T__3) {
				{
				{
				setState(125);
				match(T__3);
				setState(128);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,14,_ctx) ) {
				case 1:
					{
					setState(126);
					espressione(0);
					}
					break;
				case 2:
					{
					setState(127);
					condizione(0);
					}
					break;
				}
				}
				}
				setState(134);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class CondizioneContext extends ParserRuleContext {
		public CondizioneContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_condizione; }
	 
		public CondizioneContext() { }
		public void copyFrom(CondizioneContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ParentesiCondizioneContext extends CondizioneContext {
		public CondizioneContext condizione() {
			return getRuleContext(CondizioneContext.class,0);
		}
		public ParentesiCondizioneContext(CondizioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class BooleanoContext extends CondizioneContext {
		public BooleanoContext(CondizioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class LogicoContext extends CondizioneContext {
		public List<CondizioneContext> condizione() {
			return getRuleContexts(CondizioneContext.class);
		}
		public CondizioneContext condizione(int i) {
			return getRuleContext(CondizioneContext.class,i);
		}
		public LogicoContext(CondizioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ConfrontoContext extends CondizioneContext {
		public List<EspressioneContext> espressione() {
			return getRuleContexts(EspressioneContext.class);
		}
		public EspressioneContext espressione(int i) {
			return getRuleContext(EspressioneContext.class,i);
		}
		public ConfrontoContext(CondizioneContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class NegazioneContext extends CondizioneContext {
		public CondizioneContext condizione() {
			return getRuleContext(CondizioneContext.class,0);
		}
		public NegazioneContext(CondizioneContext ctx) { copyFrom(ctx); }
	}

	public final CondizioneContext condizione() throws RecognitionException {
		return condizione(0);
	}

	private CondizioneContext condizione(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		CondizioneContext _localctx = new CondizioneContext(_ctx, _parentState);
		CondizioneContext _prevctx = _localctx;
		int _startState = 20;
		enterRecursionRule(_localctx, 20, RULE_condizione, _p);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(147);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,16,_ctx) ) {
			case 1:
				{
				_localctx = new NegazioneContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;

				setState(136);
				match(T__22);
				setState(137);
				condizione(4);
				}
				break;
			case 2:
				{
				_localctx = new ConfrontoContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(138);
				espressione(0);
				setState(139);
				_la = _input.LA(1);
				if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 520093696L) != 0)) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(140);
				espressione(0);
				}
				break;
			case 3:
				{
				_localctx = new BooleanoContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(142);
				_la = _input.LA(1);
				if ( !(_la==T__28 || _la==T__29) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
				break;
			case 4:
				{
				_localctx = new ParentesiCondizioneContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(143);
				match(T__1);
				setState(144);
				condizione(0);
				setState(145);
				match(T__2);
				}
				break;
			}
			_ctx.stop = _input.LT(-1);
			setState(154);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,17,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					{
					_localctx = new LogicoContext(new CondizioneContext(_parentctx, _parentState));
					pushNewRecursionContext(_localctx, _startState, RULE_condizione);
					setState(149);
					if (!(precpred(_ctx, 5))) throw new FailedPredicateException(this, "precpred(_ctx, 5)");
					setState(150);
					_la = _input.LA(1);
					if ( !(_la==T__20 || _la==T__21) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					setState(151);
					condizione(6);
					}
					} 
				}
				setState(156);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,17,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	public boolean sempred(RuleContext _localctx, int ruleIndex, int predIndex) {
		switch (ruleIndex) {
		case 8:
			return espressione_sempred((EspressioneContext)_localctx, predIndex);
		case 10:
			return condizione_sempred((CondizioneContext)_localctx, predIndex);
		}
		return true;
	}
	private boolean espressione_sempred(EspressioneContext _localctx, int predIndex) {
		switch (predIndex) {
		case 0:
			return precpred(_ctx, 9);
		case 1:
			return precpred(_ctx, 7);
		case 2:
			return precpred(_ctx, 6);
		case 3:
			return precpred(_ctx, 5);
		case 4:
			return precpred(_ctx, 11);
		}
		return true;
	}
	private boolean condizione_sempred(CondizioneContext _localctx, int predIndex) {
		switch (predIndex) {
		case 5:
			return precpred(_ctx, 5);
		}
		return true;
	}

	public static final String _serializedATN =
		"\u0004\u0001#\u009e\u0002\u0000\u0007\u0000\u0002\u0001\u0007\u0001\u0002"+
		"\u0002\u0007\u0002\u0002\u0003\u0007\u0003\u0002\u0004\u0007\u0004\u0002"+
		"\u0005\u0007\u0005\u0002\u0006\u0007\u0006\u0002\u0007\u0007\u0007\u0002"+
		"\b\u0007\b\u0002\t\u0007\t\u0002\n\u0007\n\u0001\u0000\u0004\u0000\u0018"+
		"\b\u0000\u000b\u0000\f\u0000\u0019\u0001\u0000\u0001\u0000\u0001\u0001"+
		"\u0001\u0001\u0001\u0001\u0001\u0001\u0003\u0001\"\b\u0001\u0001\u0001"+
		"\u0001\u0001\u0001\u0001\u0001\u0002\u0001\u0002\u0001\u0002\u0005\u0002"+
		"*\b\u0002\n\u0002\f\u0002-\t\u0002\u0001\u0003\u0001\u0003\u0001\u0003"+
		"\u0005\u00032\b\u0003\n\u0003\f\u00035\t\u0003\u0001\u0003\u0001\u0003"+
		"\u0001\u0004\u0001\u0004\u0001\u0004\u0003\u0004<\b\u0004\u0001\u0005"+
		"\u0001\u0005\u0001\u0005\u0001\u0005\u0003\u0005B\b\u0005\u0001\u0006"+
		"\u0001\u0006\u0001\u0006\u0001\u0006\u0001\u0006\u0001\u0006\u0001\u0006"+
		"\u0003\u0006K\b\u0006\u0001\u0007\u0001\u0007\u0001\u0007\u0003\u0007"+
		"P\b\u0007\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001"+
		"\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0003\ba\b"+
		"\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001"+
		"\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0003\br\b\b\u0001"+
		"\b\u0005\bu\b\b\n\b\f\bx\t\b\u0001\t\u0001\t\u0003\t|\b\t\u0001\t\u0001"+
		"\t\u0001\t\u0003\t\u0081\b\t\u0005\t\u0083\b\t\n\t\f\t\u0086\t\t\u0001"+
		"\n\u0001\n\u0001\n\u0001\n\u0001\n\u0001\n\u0001\n\u0001\n\u0001\n\u0001"+
		"\n\u0001\n\u0001\n\u0003\n\u0094\b\n\u0001\n\u0001\n\u0001\n\u0005\n\u0099"+
		"\b\n\n\n\f\n\u009c\t\n\u0001\n\u0000\u0002\u0010\u0014\u000b\u0000\u0002"+
		"\u0004\u0006\b\n\f\u000e\u0010\u0012\u0014\u0000\u0006\u0001\u0000\u000b"+
		"\f\u0001\u0000\u000e\u000f\u0001\u0000\u0010\u0012\u0001\u0000\u0018\u001c"+
		"\u0001\u0000\u001d\u001e\u0001\u0000\u0015\u0016\u00ae\u0000\u0017\u0001"+
		"\u0000\u0000\u0000\u0002\u001d\u0001\u0000\u0000\u0000\u0004&\u0001\u0000"+
		"\u0000\u0000\u0006.\u0001\u0000\u0000\u0000\b;\u0001\u0000\u0000\u0000"+
		"\n=\u0001\u0000\u0000\u0000\fC\u0001\u0000\u0000\u0000\u000eL\u0001\u0000"+
		"\u0000\u0000\u0010`\u0001\u0000\u0000\u0000\u0012{\u0001\u0000\u0000\u0000"+
		"\u0014\u0093\u0001\u0000\u0000\u0000\u0016\u0018\u0003\u0002\u0001\u0000"+
		"\u0017\u0016\u0001\u0000\u0000\u0000\u0018\u0019\u0001\u0000\u0000\u0000"+
		"\u0019\u0017\u0001\u0000\u0000\u0000\u0019\u001a\u0001\u0000\u0000\u0000"+
		"\u001a\u001b\u0001\u0000\u0000\u0000\u001b\u001c\u0005\u0000\u0000\u0001"+
		"\u001c\u0001\u0001\u0000\u0000\u0000\u001d\u001e\u0005\u0001\u0000\u0000"+
		"\u001e\u001f\u0005\u001f\u0000\u0000\u001f!\u0005\u0002\u0000\u0000 \""+
		"\u0003\u0004\u0002\u0000! \u0001\u0000\u0000\u0000!\"\u0001\u0000\u0000"+
		"\u0000\"#\u0001\u0000\u0000\u0000#$\u0005\u0003\u0000\u0000$%\u0003\u0006"+
		"\u0003\u0000%\u0003\u0001\u0000\u0000\u0000&+\u0005\u001f\u0000\u0000"+
		"\'(\u0005\u0004\u0000\u0000(*\u0005\u001f\u0000\u0000)\'\u0001\u0000\u0000"+
		"\u0000*-\u0001\u0000\u0000\u0000+)\u0001\u0000\u0000\u0000+,\u0001\u0000"+
		"\u0000\u0000,\u0005\u0001\u0000\u0000\u0000-+\u0001\u0000\u0000\u0000"+
		".3\u0005\u0005\u0000\u0000/2\u0003\b\u0004\u000002\u0003\u0006\u0003\u0000"+
		"1/\u0001\u0000\u0000\u000010\u0001\u0000\u0000\u000025\u0001\u0000\u0000"+
		"\u000031\u0001\u0000\u0000\u000034\u0001\u0000\u0000\u000046\u0001\u0000"+
		"\u0000\u000053\u0001\u0000\u0000\u000067\u0005\u0006\u0000\u00007\u0007"+
		"\u0001\u0000\u0000\u00008<\u0003\n\u0005\u00009<\u0003\f\u0006\u0000:"+
		"<\u0003\u000e\u0007\u0000;8\u0001\u0000\u0000\u0000;9\u0001\u0000\u0000"+
		"\u0000;:\u0001\u0000\u0000\u0000<\t\u0001\u0000\u0000\u0000=>\u0005\u001f"+
		"\u0000\u0000>A\u0005\u0007\u0000\u0000?B\u0003\u0010\b\u0000@B\u0003\u0014"+
		"\n\u0000A?\u0001\u0000\u0000\u0000A@\u0001\u0000\u0000\u0000B\u000b\u0001"+
		"\u0000\u0000\u0000CD\u0005\b\u0000\u0000DE\u0005\u0002\u0000\u0000EF\u0003"+
		"\u0014\n\u0000FG\u0005\u0003\u0000\u0000GJ\u0003\u0006\u0003\u0000HI\u0005"+
		"\t\u0000\u0000IK\u0003\u0006\u0003\u0000JH\u0001\u0000\u0000\u0000JK\u0001"+
		"\u0000\u0000\u0000K\r\u0001\u0000\u0000\u0000LO\u0005\n\u0000\u0000MP"+
		"\u0003\u0010\b\u0000NP\u0003\u0014\n\u0000OM\u0001\u0000\u0000\u0000O"+
		"N\u0001\u0000\u0000\u0000P\u000f\u0001\u0000\u0000\u0000QR\u0006\b\uffff"+
		"\uffff\u0000RS\u0007\u0000\u0000\u0000ST\u0005\u0002\u0000\u0000TU\u0003"+
		"\u0010\b\u0000UV\u0005\u0003\u0000\u0000Va\u0001\u0000\u0000\u0000WX\u0007"+
		"\u0001\u0000\u0000Xa\u0003\u0010\b\bYa\u0005\u0014\u0000\u0000Za\u0005"+
		" \u0000\u0000[a\u0005\u001f\u0000\u0000\\]\u0005\u0002\u0000\u0000]^\u0003"+
		"\u0010\b\u0000^_\u0005\u0003\u0000\u0000_a\u0001\u0000\u0000\u0000`Q\u0001"+
		"\u0000\u0000\u0000`W\u0001\u0000\u0000\u0000`Y\u0001\u0000\u0000\u0000"+
		"`Z\u0001\u0000\u0000\u0000`[\u0001\u0000\u0000\u0000`\\\u0001\u0000\u0000"+
		"\u0000av\u0001\u0000\u0000\u0000bc\n\t\u0000\u0000cd\u0005\r\u0000\u0000"+
		"du\u0003\u0010\b\tef\n\u0007\u0000\u0000fg\u0007\u0002\u0000\u0000gu\u0003"+
		"\u0010\b\bhi\n\u0006\u0000\u0000ij\u0007\u0001\u0000\u0000ju\u0003\u0010"+
		"\b\u0007kl\n\u0005\u0000\u0000lm\u0005\u0013\u0000\u0000mu\u0003\u0010"+
		"\b\u0005no\n\u000b\u0000\u0000oq\u0005\u0002\u0000\u0000pr\u0003\u0012"+
		"\t\u0000qp\u0001\u0000\u0000\u0000qr\u0001\u0000\u0000\u0000rs\u0001\u0000"+
		"\u0000\u0000su\u0005\u0003\u0000\u0000tb\u0001\u0000\u0000\u0000te\u0001"+
		"\u0000\u0000\u0000th\u0001\u0000\u0000\u0000tk\u0001\u0000\u0000\u0000"+
		"tn\u0001\u0000\u0000\u0000ux\u0001\u0000\u0000\u0000vt\u0001\u0000\u0000"+
		"\u0000vw\u0001\u0000\u0000\u0000w\u0011\u0001\u0000\u0000\u0000xv\u0001"+
		"\u0000\u0000\u0000y|\u0003\u0010\b\u0000z|\u0003\u0014\n\u0000{y\u0001"+
		"\u0000\u0000\u0000{z\u0001\u0000\u0000\u0000|\u0084\u0001\u0000\u0000"+
		"\u0000}\u0080\u0005\u0004\u0000\u0000~\u0081\u0003\u0010\b\u0000\u007f"+
		"\u0081\u0003\u0014\n\u0000\u0080~\u0001\u0000\u0000\u0000\u0080\u007f"+
		"\u0001\u0000\u0000\u0000\u0081\u0083\u0001\u0000\u0000\u0000\u0082}\u0001"+
		"\u0000\u0000\u0000\u0083\u0086\u0001\u0000\u0000\u0000\u0084\u0082\u0001"+
		"\u0000\u0000\u0000\u0084\u0085\u0001\u0000\u0000\u0000\u0085\u0013\u0001"+
		"\u0000\u0000\u0000\u0086\u0084\u0001\u0000\u0000\u0000\u0087\u0088\u0006"+
		"\n\uffff\uffff\u0000\u0088\u0089\u0005\u0017\u0000\u0000\u0089\u0094\u0003"+
		"\u0014\n\u0004\u008a\u008b\u0003\u0010\b\u0000\u008b\u008c\u0007\u0003"+
		"\u0000\u0000\u008c\u008d\u0003\u0010\b\u0000\u008d\u0094\u0001\u0000\u0000"+
		"\u0000\u008e\u0094\u0007\u0004\u0000\u0000\u008f\u0090\u0005\u0002\u0000"+
		"\u0000\u0090\u0091\u0003\u0014\n\u0000\u0091\u0092\u0005\u0003\u0000\u0000"+
		"\u0092\u0094\u0001\u0000\u0000\u0000\u0093\u0087\u0001\u0000\u0000\u0000"+
		"\u0093\u008a\u0001\u0000\u0000\u0000\u0093\u008e\u0001\u0000\u0000\u0000"+
		"\u0093\u008f\u0001\u0000\u0000\u0000\u0094\u009a\u0001\u0000\u0000\u0000"+
		"\u0095\u0096\n\u0005\u0000\u0000\u0096\u0097\u0007\u0005\u0000\u0000\u0097"+
		"\u0099\u0003\u0014\n\u0006\u0098\u0095\u0001\u0000\u0000\u0000\u0099\u009c"+
		"\u0001\u0000\u0000\u0000\u009a\u0098\u0001\u0000\u0000\u0000\u009a\u009b"+
		"\u0001\u0000\u0000\u0000\u009b\u0015\u0001\u0000\u0000\u0000\u009c\u009a"+
		"\u0001\u0000\u0000\u0000\u0012\u0019!+13;AJO`qtv{\u0080\u0084\u0093\u009a";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}