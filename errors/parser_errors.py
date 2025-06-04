"""
Sistema di gestione degli errori per il parser Saltino.

Questo modulo definisce eccezioni personalizzate e classi di errore
specifiche per fornire informazioni dettagliate sugli errori di parsing.
"""

from typing import Optional, List, Any


class SourcePosition:
    """Rappresenta una posizione nel codice sorgente."""

    def __init__(self, line: int, column: int, char_position: Optional[int] = None):
        self.line = line
        self.column = column
        self.char_position = char_position

    def __str__(self) -> str:
        if self.char_position is not None:
            return f"linea {self.line}, colonna {self.column} (posizione {self.char_position})"
        return f"linea {self.line}, colonna {self.column}"

    def __repr__(self) -> str:
        return f"SourcePosition({self.line}, {self.column}, {self.char_position})"


class SaltinoError(Exception):
    """Classe base per tutti gli errori Saltino."""

    def __init__(self, message: str, position: Optional[SourcePosition] = None):
        self.message = message
        self.position = position
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.position:
            return f"Errore alla {self.position}: {self.message}"
        return f"Errore: {self.message}"


class SaltinoParseError(SaltinoError):
    """Errore di parsing del codice sorgente."""

    def __init__(self, message: str, position: Optional[SourcePosition] = None,
                 offending_symbol: Optional[str] = None, expected_tokens: Optional[List[str]] = None):
        self.offending_symbol = offending_symbol
        self.expected_tokens = expected_tokens or []

        # Arricchisci il messaggio con informazioni aggiuntive
        enhanced_message = self._enhance_message(message)
        super().__init__(enhanced_message, position)

    def _enhance_message(self, message: str) -> str:
        enhanced = message

        if self.offending_symbol:
            enhanced += f" Trovato: '{self.offending_symbol}'"

        if self.expected_tokens:
            if len(self.expected_tokens) == 1:
                enhanced += f" Atteso: '{self.expected_tokens[0]}'"
            else:
                tokens_str = "', '".join(self.expected_tokens)
                enhanced += f" Attesi uno tra: '{tokens_str}'"

        return enhanced


class SaltinoLexicalError(SaltinoError):
    """Errore lessicale (riconoscimento token)."""

    def __init__(self, message: str, position: Optional[SourcePosition] = None,
                 invalid_char: Optional[str] = None):
        self.invalid_char = invalid_char

        enhanced_message = message
        if invalid_char:
            enhanced_message += f" Carattere non valido: '{invalid_char}'"

        super().__init__(enhanced_message, position)

    def get_recovery_suggestions(self) -> List[str]:
        """
        Genera suggerimenti specifici per il recupero dall'errore lessicale.

        Returns:
            Lista di suggerimenti per correggere l'errore
        """
        suggestions = []

        if self.invalid_char:
            char = self.invalid_char

            # Suggerimenti specifici per caratteri comuni
            if char == '@':
                suggestions.append(
                    "Sostituisci '@' con un operatore valido: +, -, *, /, %, ^")
                suggestions.append(
                    "Se stai cercando di elevare a potenza, usa '^' invece di '@'")
            elif char == '#':
                suggestions.append("I commenti non sono supportati in Saltino")
                suggestions.append(
                    "Rimuovi il carattere '#' e il testo che segue")
            elif char == '$':
                suggestions.append("Il carattere '$' non è supportato")
                suggestions.append(
                    "Usa identificatori normali senza caratteri speciali")
            elif char == '&':
                suggestions.append(
                    "Usa 'and' invece di '&' per l'operatore logico AND")
            elif char == '|':
                suggestions.append(
                    "Usa 'or' invece di '|' per l'operatore logico OR")
            elif char == '!':
                suggestions.append(
                    "Usa 'not' invece di '!' per la negazione logica")
            elif char in ['"', "'"]:
                suggestions.append(
                    "Le stringhe non sono supportate in Saltino")
                suggestions.append(
                    "Usa solo numeri interi, liste di interi e valori booleani")
            elif char.isdigit() and self.position:
                suggestions.append(
                    "Controlla che il numero sia scritto correttamente")
                suggestions.append(
                    "Assicurati che non ci siano spazi all'interno del numero")
            else:
                suggestions.append(f"Rimuovi il carattere '{char}' non valido")
                suggestions.append("Controlla la sintassi nella zona indicata")

        # Suggerimenti generali
        if not suggestions:
            suggestions.append(
                "Verifica la sintassi del codice nell'area indicata")
            suggestions.append(
                "Controlla che tutti i caratteri utilizzati siano supportati da Saltino")

        return suggestions


class SaltinoSyntaxError(SaltinoParseError):
    """Errore di sintassi specifico."""

    def __init__(self, message: str, position: Optional[SourcePosition] = None,
                 rule_context: Optional[str] = None, **kwargs):
        self.rule_context = rule_context

        enhanced_message = message
        if rule_context:
            enhanced_message = f"Errore di sintassi in {rule_context}: {message}"

        super().__init__(enhanced_message, position, **kwargs)


class SaltinoSemanticError(SaltinoError):
    """Errore semantico (costruzione AST)."""

    def __init__(self, message: str, position: Optional[SourcePosition] = None,
                 node_type: Optional[str] = None):
        self.node_type = node_type

        enhanced_message = message
        if node_type:
            enhanced_message = f"Errore semantico nel nodo {node_type}: {message}"

        super().__init__(enhanced_message, position)


class ErrorSeverity:
    """Livelli di severità degli errori."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class ErrorReport:
    """Rappresenta un report di errore dettagliato."""

    def __init__(self, severity: str, error: SaltinoError,
                 recovery_suggestion: Optional[str] = None):
        self.severity = severity
        self.error = error
        self.recovery_suggestion = recovery_suggestion
        self.timestamp = None

    def __str__(self) -> str:
        result = f"[{self.severity}] {self.error}"
        if self.recovery_suggestion:
            result += f"\nSuggerimento: {self.recovery_suggestion}"
        return result


class ErrorCollector:
    """Raccoglie e gestisce gli errori durante il parsing."""

    def __init__(self):
        self.errors: List[ErrorReport] = []
        self.has_fatal_errors = False

    def add_error(self, error: SaltinoError, severity: str = ErrorSeverity.ERROR,
                  recovery_suggestion: Optional[str] = None):
        """Aggiunge un errore alla collezione."""
        report = ErrorReport(severity, error, recovery_suggestion)
        self.errors.append(report)

        if severity == ErrorSeverity.FATAL:
            self.has_fatal_errors = True

    def add_lexical_error(self, message: str, line: int, column: int,
                          invalid_char: Optional[str] = None,
                          severity: str = ErrorSeverity.ERROR):
        """Aggiunge un errore lessicale."""
        position = SourcePosition(line, column)
        error = SaltinoLexicalError(message, position, invalid_char)

        suggestion = None
        if invalid_char:
            suggestion = f"Rimuovi o sostituisci il carattere '{invalid_char}'"

        self.add_error(error, severity, suggestion)

    def add_syntax_error(self, message: str, line: int, column: int,
                         offending_symbol: Optional[str] = None,
                         expected_tokens: Optional[List[str]] = None,
                         rule_context: Optional[str] = None,
                         severity: str = ErrorSeverity.ERROR):
        """Aggiunge un errore di sintassi."""
        position = SourcePosition(line, column)
        error = SaltinoSyntaxError(
            message, position, rule_context,
            offending_symbol=offending_symbol,
            expected_tokens=expected_tokens
        )

        suggestion = self._generate_syntax_suggestion(
            offending_symbol, expected_tokens)
        self.add_error(error, severity, suggestion)

    def add_semantic_error(self, message: str, line: int, column: int,
                           node_type: Optional[str] = None,
                           severity: str = ErrorSeverity.ERROR):
        """Aggiunge un errore semantico."""
        position = SourcePosition(line, column)
        error = SaltinoSemanticError(message, position, node_type)
        self.add_error(error, severity)

    def add_unbound_local_error(self, message: str, line: int, column: int,
                                variable_name: Optional[str] = None,
                                severity: str = ErrorSeverity.ERROR):
        """Aggiunge un errore di variabile locale non inizializzata."""
        position = SourcePosition(line, column)
        enhanced_message = f"UnboundLocalError: {message}"
        if variable_name:
            enhanced_message = f"UnboundLocalError for variable '{variable_name}': {message}"
        error = SaltinoSemanticError(enhanced_message, position, "variable_reference")
        self.add_error(error, severity)

    def _generate_syntax_suggestion(self, offending_symbol: Optional[str],
                                    expected_tokens: Optional[List[str]]) -> Optional[str]:
        """Genera un suggerimento per errori di sintassi."""
        if not expected_tokens:
            return None

        if len(expected_tokens) == 1:
            expected = expected_tokens[0]
            if offending_symbol:
                return f"Sostituisci '{offending_symbol}' con '{expected}'"
            else:
                return f"Aggiungi '{expected}'"

        tokens_list = "', '".join(expected_tokens)
        return f"Usa uno tra: '{tokens_list}'"

    def has_errors(self) -> bool:
        """Verifica se ci sono errori."""
        return len(self.errors) > 0

    def get_error_count(self) -> int:
        """Restituisce il numero di errori."""
        return len(self.errors)

    def get_errors_by_severity(self, severity: str) -> List[ErrorReport]:
        """Restituisce gli errori di una specifica severità."""
        return [err for err in self.errors if err.severity == severity]

    def clear(self):
        """Pulisce tutti gli errori."""
        self.errors.clear()
        self.has_fatal_errors = False

    def format_errors(self) -> str:
        """Formatta tutti gli errori in una stringa."""
        if not self.errors:
            return "Nessun errore."

        result = f"Trovati {len(self.errors)} errore/i:\n"
        for i, error_report in enumerate(self.errors, 1):
            result += f"\n{i}. {error_report}\n"

        return result

    def __str__(self) -> str:
        return self.format_errors()

    def get_error_report(self) -> 'ErrorCollector':
        """Restituisce un oggetto che rappresenta il report degli errori."""
        return self

    def has_warnings(self) -> bool:
        """Verifica se ci sono warning."""
        return any(err.severity == ErrorSeverity.WARNING for err in self.errors)

    def get_warnings(self) -> List[ErrorReport]:
        """Restituisce tutti i warning."""
        return [err for err in self.errors if err.severity == ErrorSeverity.WARNING]

    def format_report(self) -> str:
        """Formatta il report degli errori in modo dettagliato."""
        if not self.errors:
            return "Nessun errore rilevato."

        lines = []
        error_count = 0
        warning_count = 0

        for error_report in self.errors:
            if error_report.severity == ErrorSeverity.ERROR or error_report.severity == ErrorSeverity.FATAL:
                error_count += 1
                lines.append(f"❌ {error_report}")
            elif error_report.severity == ErrorSeverity.WARNING:
                warning_count += 1
                lines.append(f"⚠️  {error_report}")
            else:
                lines.append(f"ℹ️  {error_report}")

        header = []
        if error_count > 0:
            header.append(f"{error_count} errore/i")
        if warning_count > 0:
            header.append(f"{warning_count} warning")

        result = f"Report: {', '.join(header)}\n"
        result += "\n".join(lines)

        return result
