"""
Custom Error Listener per il parser Saltino.

Error listener semplice che override dei metodi base di ANTLR ErrorListener.
"""

from antlr4.error.ErrorListener import ErrorListener
from typing import List


class SaltinoErrorListener(ErrorListener):
    """
    Error listener semplice per il parser Saltino.

    Raccoglie gli errori di parsing in modo diretto.
    """

    def __init__(self):
        """Inizializza l'error listener."""
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """
        Override del metodo syntaxError di ErrorListener.

        Args:
            recognizer: Il parser o lexer che ha rilevato l'errore
            offendingSymbol: Il token che ha causato l'errore
            line: Numero di riga dell'errore (1-based)
            column: Colonna dell'errore (0-based)
            msg: Messaggio di errore di ANTLR
            e: Eccezione originale (se presente)
        """
        # Crea un messaggio di errore user-friendly
        error_msg = self._format_error_message(
            recognizer, offendingSymbol, line, column, msg)

        # Aggiungi l'errore alla lista
        self.errors.append({
            'line': line,
            'column': column,
            'message': error_msg,
            'type': 'syntax',
            'recognizer_type': type(recognizer).__name__,
            'offending_symbol': offendingSymbol.text if offendingSymbol else None
        })

    def _format_error_message(self, recognizer, offending_symbol, line, column, msg):
        """
        Formatta il messaggio di errore in modo user-friendly.

        Args:
            recognizer: Il parser o lexer
            offending_symbol: Il token offendente
            line: Numero di riga
            column: Numero di colonna
            msg: Messaggio originale di ANTLR

        Returns:
            Messaggio di errore formattato
        """
        recognizer_type = type(recognizer).__name__

        # Determina se è un errore del lexer o del parser
        if 'Lexer' in recognizer_type:
            return self._format_lexer_error(msg, offending_symbol)
        else:
            return self._format_parser_error(msg, offending_symbol)

    def _format_lexer_error(self, msg, offending_symbol):
        """Formatta errori del lexer."""
        # Per gli errori del lexer, il symbol spesso è None, ma possiamo estrarre il carattere dal messaggio
        symbol_text = None
        if offending_symbol and hasattr(offending_symbol, 'text'):
            symbol_text = offending_symbol.text

        # Estrai il carattere dal messaggio se non è disponibile nel symbol
        if not symbol_text and "token recognition error at:" in msg:
            # Il messaggio è tipo "token recognition error at: '@'"
            start = msg.find("'")
            if start != -1:
                end = msg.find("'", start + 1)
                if end != -1:
                    symbol_text = msg[start + 1:end]

        # Gestione di caratteri comuni problematici
        if "token recognition error" in msg.lower():
            if symbol_text == '@':
                return "Carattere '@' non supportato. Usa operatori validi come +, -, *, /"
            elif symbol_text == '#':
                return "Carattere '#' non supportato. I commenti sono con // o /* */"
            elif symbol_text == '$':
                return "Carattere '$' non supportato"
            elif symbol_text == ';':
                return "Carattere ';' non supportato. Saltino non usa il punto e virgola"
            elif symbol_text and symbol_text.isalpha():
                return f"Carattere '{symbol_text}' non riconosciuto"
            elif symbol_text:
                return f"Carattere non valido: '{symbol_text}'"
            else:
                return "Carattere non riconosciuto nel codice"

        if "unterminated string" in msg.lower():
            return "Stringa non terminata - manca la virgoletta di chiusura"

        return f"Errore lessicale: {msg}"

    def _format_parser_error(self, msg, offending_symbol):
        """Formatta errori del parser."""
        symbol_text = offending_symbol.text if offending_symbol else "EOF"

        # Traduzioni comuni per errori missing
        if "missing" in msg.lower():
            if "'def'" in msg:
                return f"Manca la parola chiave 'def' per la definizione di funzione"
            elif "'='" in msg:
                return f"Manca il simbolo di assegnamento '=' - trovato '{symbol_text}'"
            elif "'}'" in msg:
                return "Manca la parentesi graffa di chiusura '}'"
            elif "')'" in msg:
                return "Manca la parentesi tonda di chiusura ')'"
            elif "'('" in msg:
                return "Manca la parentesi tonda di apertura '('"
            elif "'{'" in msg:
                return "Manca la parentesi graffa di apertura '{'"

        # Check for extraneous input first (more specific)
        if "extraneous input" in msg.lower():
            if symbol_text.isdigit():
                return f"Numero '{symbol_text}' inaspettato - manca un operatore prima di questo numero"
            else:
                return f"Token inaspettato: '{symbol_text}'"

        # Riconoscimento di errori specifici per operatori mancanti
        if "expecting" in msg.lower() and any(op in msg for op in ["'+'", "'-'", "'*'", "'/'", "'%'"]):
            return f"Manca un operatore tra i valori - trovato '{symbol_text}'"

        # Traduzioni per errori expecting (più generici)
        if "expecting" in msg.lower():
            if "'def'" in msg:
                return f"Attesa parola chiave 'def' per definire una funzione, trovato '{symbol_text}'"
            elif "'{'" in msg:
                return "Attesa parentesi graffa di apertura '{'"
            elif "'('" in msg:
                return "Attesa parentesi tonda di apertura '('"
            elif "'='" in msg:
                return f"Atteso simbolo di assegnamento '=', trovato '{symbol_text}'"

        if "mismatched input" in msg.lower():
            if symbol_text.isdigit():
                return f"Numero '{symbol_text}' in posizione non valida - potrebbe mancare un operatore"
            else:
                return f"Token non corrispondente: '{symbol_text}'"

        if "no viable alternative" in msg.lower():
            return f"Sintassi non valida in corrispondenza di '{symbol_text}'"

        return f"Errore di sintassi: {msg}"

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        """Override del metodo reportAmbiguity - di solito non serve per errori utente."""
        pass

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        """Override del metodo reportAttemptingFullContext - informazione di debug."""
        pass

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        """Override del metodo reportContextSensitivity - informazione di debug."""
        pass

    def has_errors(self):
        """Restituisce True se ci sono stati errori."""
        return len(self.errors) > 0

    def get_errors(self):
        """Restituisce la lista degli errori."""
        return self.errors

    def get_error_count(self):
        """Restituisce il numero di errori."""
        return len(self.errors)

    def print_errors(self):
        """Stampa tutti gli errori in formato leggibile."""
        for error in self.errors:
            print(
                f"Errore alla riga {error['line']}, colonna {error['column']}: {error['message']}")

    def clear_errors(self):
        """Pulisce la lista degli errori."""
        self.errors.clear()


def create_error_listener():
    """
    Factory function per creare un error listener.

    Returns:
        Un'istanza di SaltinoErrorListener
    """
    return SaltinoErrorListener()
