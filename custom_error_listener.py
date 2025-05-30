"""
Custom Error Listener per il parser Saltino.

Questo modulo implementa error listener personalizzati per ANTLR
che si integrano con il sistema di errori personalizzato definito in parser_errors.py.
"""

from antlr4.error.ErrorListener import ErrorListener
from antlr4 import ParserRuleContext, Token
from parser_errors import (
    SourcePosition, SaltinoParseError, SaltinoLexicalError,
    SaltinoSyntaxError, ErrorCollector, ErrorSeverity
)
from typing import Optional, List, Any


class SaltinoErrorListener(ErrorListener):
    """
    Error listener personalizzato per il parser Saltino.

    Raccoglie gli errori di parsing e li trasforma in eccezioni personalizzate
    utilizzando il sistema di errori definito in parser_errors.py.
    """

    def __init__(self, error_collector: Optional[ErrorCollector] = None):
        """
        Inizializza l'error listener.

        Args:
            error_collector: Collettore di errori condiviso. Se None, ne crea uno nuovo.
        """
        super().__init__()
        self.error_collector = error_collector or ErrorCollector()
        self._error_count = 0

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """
        Chiamato quando ANTLR rileva un errore di sintassi.

        Args:
            recognizer: Il parser o lexer che ha rilevato l'errore
            offendingSymbol: Il token che ha causato l'errore
            line: Numero di riga dell'errore
            column: Colonna dell'errore
            msg: Messaggio di errore di ANTLR
            e: Eccezione originale (se presente)
        """
        self._error_count += 1
        position = SourcePosition(line, column)

        # Determina il tipo di errore basandosi sul riconoscitore
        if hasattr(recognizer, 'getRuleNames'):
            # È un parser error
            error = self._create_parser_error(
                msg, position, offendingSymbol, e)
        else:
            # È un lexer error
            error = self._create_lexer_error(msg, position, offendingSymbol)

        # Aggiungi l'errore al collettore
        self.error_collector.add_error(error, ErrorSeverity.ERROR)

    def _create_parser_error(self, msg: str, position: SourcePosition,
                             offending_symbol, exception) -> SaltinoSyntaxError:
        """
        Crea un errore di sintassi dal messaggio del parser.

        Args:
            msg: Messaggio di errore originale
            position: Posizione dell'errore
            offending_symbol: Token che ha causato l'errore
            exception: Eccezione originale di ANTLR
        """
        # Estrai informazioni dal token offendente
        offending_text = None
        if offending_symbol and hasattr(offending_symbol, 'text'):
            offending_text = offending_symbol.text

        # Analizza il messaggio per estrarre token attesi
        expected_tokens = self._extract_expected_tokens(msg)

        # Crea un messaggio di errore più user-friendly
        enhanced_msg = self._enhance_parser_error_message(
            msg, offending_text, expected_tokens)

        return SaltinoSyntaxError(
            message=enhanced_msg,
            position=position,
            offending_symbol=offending_text,
            expected_tokens=expected_tokens
        )

    def _create_lexer_error(self, msg: str, position: SourcePosition,
                            offending_symbol) -> SaltinoLexicalError:
        """
        Crea un errore lessicale dal messaggio del lexer.

        Args:
            msg: Messaggio di errore originale
            position: Posizione dell'errore
            offending_symbol: Carattere/i che hanno causato l'errore
        """
        # Estrai il carattere offendente
        offending_char = None
        if offending_symbol and hasattr(offending_symbol, 'text'):
            offending_char = offending_symbol.text

        # Crea un messaggio di errore più user-friendly
        enhanced_msg = self._enhance_lexer_error_message(msg, offending_char)

        return SaltinoLexicalError(
            message=enhanced_msg,
            position=position,
            invalid_char=offending_char
        )

    def _extract_expected_tokens(self, msg: str) -> List[str]:
        """
        Estrae i token attesi dal messaggio di errore di ANTLR.

        Args:
            msg: Messaggio di errore di ANTLR

        Returns:
            Lista dei token attesi
        """
        expected_tokens = []

        # ANTLR spesso include messaggi come "expecting {'if', 'while', '}'}"
        if "expecting" in msg.lower():
            # Estrai il contenuto tra parentesi graffe
            start = msg.find('{')
            end = msg.find('}')
            if start != -1 and end != -1:
                tokens_str = msg[start+1:end]
                # Dividi per virgola e pulisci
                tokens = [token.strip().strip("'\"")
                          for token in tokens_str.split(',')]
                expected_tokens.extend(tokens)

        return expected_tokens

    def _enhance_parser_error_message(self, original_msg: str, offending_text: Optional[str],
                                      expected_tokens: List[str]) -> str:
        """
        Migliora il messaggio di errore del parser per renderlo più user-friendly.

        Args:
            original_msg: Messaggio originale di ANTLR
            offending_text: Testo del token offendente
            expected_tokens: Token attesi

        Returns:
            Messaggio di errore migliorato
        """
        # Messaggi di errore comuni in italiano
        error_translations = {
            "missing": "mancante",
            "expecting": "atteso",
            "extraneous input": "input non riconosciuto",
            "mismatched input": "input non corrispondente",
            "no viable alternative": "sintassi non valida"
        }

        # Sostituisci termini comuni
        enhanced_msg = original_msg.lower()
        for english, italian in error_translations.items():
            enhanced_msg = enhanced_msg.replace(english, italian)

        # Aggiungi informazioni specifiche
        if offending_text:
            enhanced_msg += f" (trovato: '{offending_text}')"

        if expected_tokens:
            if len(expected_tokens) == 1:
                enhanced_msg += f" - atteso: {expected_tokens[0]}"
            else:
                enhanced_msg += f" - attesi uno tra: {', '.join(expected_tokens)}"

        return enhanced_msg.capitalize()

    def _enhance_lexer_error_message(self, original_msg: str, offending_char: Optional[str]) -> str:
        """
        Migliora il messaggio di errore del lexer per renderlo più user-friendly.

        Args:
            original_msg: Messaggio originale di ANTLR
            offending_char: Carattere offendente

        Returns:
            Messaggio di errore migliorato
        """
        # Gestione di errori lessicali comuni
        if "token recognition error" in original_msg.lower():
            if offending_char:
                if offending_char == '@':
                    return f"Carattere '@' non supportato - usa operatori validi come +, -, *, /"
                elif offending_char == '#':
                    return f"Carattere '#' non supportato - i commenti non sono supportati"
                elif offending_char == '$':
                    return f"Carattere '$' non supportato"
                elif offending_char.isalpha():
                    return f"Carattere '{offending_char}' non riconosciuto - controlla la sintassi"
                else:
                    return f"Carattere non riconosciuto: '{offending_char}'"
            else:
                return "Carattere non riconosciuto nel codice sorgente"

        # Traduci altri messaggi comuni
        if "unterminated string" in original_msg.lower():
            return "Stringa non terminata - manca la virgoletta di chiusura"

        # Messaggio generico migliorato
        if offending_char:
            return f"Errore lessicale con carattere '{offending_char}'"

        return f"Errore lessicale: {original_msg}"

    def get_error_count(self) -> int:
        """Restituisce il numero di errori rilevati."""
        return self._error_count

    def has_errors(self) -> bool:
        """Controlla se ci sono stati errori."""
        return self._error_count > 0

    def get_error_collector(self) -> ErrorCollector:
        """Restituisce il collettore di errori."""
        return self.error_collector


class SaltinoSyntaxErrorStrategy:
    """
    Strategia di recupero dagli errori per il parser Saltino.

    Fornisce suggerimenti intelligenti per il recupero dagli errori di sintassi.
    """

    @staticmethod
    def suggest_recovery(error: SaltinoSyntaxError) -> List[str]:
        """
        Suggerisce strategie di recupero basate sul tipo di errore.

        Args:
            error: L'errore di sintassi

        Returns:
            Lista di suggerimenti per il recupero
        """
        suggestions = []

        if error.offending_symbol:
            symbol = error.offending_symbol.lower()

            # Suggerimenti basati sui token comuni
            if symbol in ['{', '}']:
                suggestions.append(
                    "Controlla che tutte le parentesi graffe siano bilanciate")
            elif symbol in ['(', ')']:
                suggestions.append(
                    "Controlla che tutte le parentesi tonde siano bilanciate")
            elif symbol == ';':
                suggestions.append(
                    "Controlla la sintassi dell'istruzione precedente")
            elif symbol == 'if':
                suggestions.append(
                    "Controlla la sintassi della condizione after 'if'")
            elif symbol == 'else':
                suggestions.append(
                    "Assicurati che 'else' sia preceduto da un 'if' valido")

        # Suggerimenti basati sui token attesi
        if error.expected_tokens:
            for token in error.expected_tokens:
                if token == ';':
                    suggestions.append("Potrebbe mancare un punto e virgola")
                elif token == '{':
                    suggestions.append(
                        "Potrebbe mancare una parentesi graffa di apertura")
                elif token == '}':
                    suggestions.append(
                        "Potrebbe mancare una parentesi graffa di chiusura")
                elif token == ')':
                    suggestions.append(
                        "Potrebbe mancare una parentesi tonda di chiusura")

        if not suggestions:
            suggestions.append(
                "Controlla la sintassi del codice nell'area indicata")

        return suggestions


def create_error_listener() -> SaltinoErrorListener:
    """
    Factory function per creare un error listener configurato.

    Returns:
        Un'istanza configurata di SaltinoErrorListener
    """
    return SaltinoErrorListener()


def create_shared_error_listener(error_collector: ErrorCollector) -> SaltinoErrorListener:
    """
    Factory function per creare un error listener che condivide un error collector.

    Args:
        error_collector: Il collettore di errori condiviso

    Returns:
        Un'istanza configurata di SaltinoErrorListener
    """
    return SaltinoErrorListener(error_collector)
