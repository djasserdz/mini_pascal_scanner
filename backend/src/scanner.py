from typing import List, Dict, Tuple
from src.model.Token import Token, ScanResult, ErrorResponse, SymbolInfo, TokenResponse
import src.automata as automata


class Scanner:
    def __init__(self, source_text: str, filename: str = "<input>"):
        self.src = source_text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.automaton = automata.Automaton()
        self.tokens: List[Token] = []
        self.symbol_table: Dict[str, Dict] = {}
        self.errors: List[Tuple[int, int, str]] = []
        self.filename = filename
        self.length = len(self.src)

    def _advance(self, n: int):
        for _ in range(n):
            if self.pos >= self.length:
                return
            ch = self.src[self.pos]
            self.pos += 1
            if ch == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1

    def _skip_whitespace(self) -> bool:
        skipped = False
        while self.pos < self.length and self.src[self.pos].isspace():
            self._advance(1)
            skipped = True
        return skipped

    def _record_symbol(self, token: Token):
        if token.type == "ID":
            if token.lexeme not in self.symbol_table:
                self.symbol_table[token.lexeme] = {
                    "first_line": token.line,
                    "first_col": token.col,
                    "occurrences": 1
                }
            else:
                self.symbol_table[token.lexeme]["occurrences"] += 1

    def _add_token(self, typ: str, lexeme: str, line: int, col: int):
        token = Token(typ, lexeme, line, col)
        self.tokens.append(token)
        self._record_symbol(token)

    def _handle_error(self, message: str, line: int, col: int):
        self.errors.append((line, col, message))

    def tokenize(self):
        while self.pos < self.length:
            if self._skip_whitespace():
                continue

            start_line = self.line
            start_col = self.col

            match = self.automaton.match(self.src, self.pos)
            if match is None:
                # Handle invalid identifiers gracefully to avoid cascading errors
                ch = self.src[self.pos]
                if automata.is_letter(ch):
                    i = self.pos + 1
                    while i < self.length and automata.is_alnum(self.src[i]):
                        i += 1
                    lexeme = self.src[self.pos:i]
                    self._handle_error(
                        f"Identificateur invalide (doit être lettre + chiffre ...): {lexeme!r}",
                        self.line,
                        self.col,
                    )
                    self._advance(i - self.pos)
                else:
                    self._handle_error(f"Illegal character: {repr(ch)}", self.line, self.col)
                    self._advance(1)
                continue

            typ, lexeme, length = match
            self._add_token(typ, lexeme, start_line, start_col)
            self._advance(length)

        self._add_token("EOF", "", self.line, self.col)

    # ✅ SEMANTIC VALIDATION
    def _validate_program_structure(self):
        if not self.tokens:
            return

        first = self.tokens[0]
        if first.type != "PROGRAMME":
            self._handle_error("Le programme doit commencer par 'programme'", first.line, first.col)

        if len(self.tokens) >= 3:
            if self.tokens[1].type != "ID":
                self._handle_error("Un identificateur est attendu après 'programme'",
                                   self.tokens[1].line, self.tokens[1].col)
            if self.tokens[2].type != "POINT_VIRGULE":
                self._handle_error("';' est attendu après le nom du programme",
                                   self.tokens[2].line, self.tokens[2].col)

        if not any(t.type == "DEBUT" for t in self.tokens):
            self._handle_error("'debut' est manquant", self.tokens[-1].line, self.tokens[-1].col)

        if not any(t.type == "FIN" for t in self.tokens):
            self._handle_error("'fin' est manquant", self.tokens[-1].line, self.tokens[-1].col)

        if len(self.tokens) >= 2:
            if self.tokens[-2].type != "POINT":
                self._handle_error("Le programme doit se terminer par '.'",
                                   self.tokens[-2].line, self.tokens[-2].col)

        self._validate_paired_keywords()

    def _validate_paired_keywords(self):
        si_stack = []
        repeter_stack = []

        for token in self.tokens:
            if token.type == "SI":
                si_stack.append(token)
            elif token.type == "ALORS":
                if not si_stack:
                    self._handle_error("'alors' sans 'si'", token.line, token.col)
                else:
                    si_stack.pop()
            elif token.type == "REPETER":
                repeter_stack.append(token)
            elif token.type == "JUSQUA":
                if not repeter_stack:
                    self._handle_error("'jusqua' sans 'repeter'", token.line, token.col)
                else:
                    repeter_stack.pop()

        for t in si_stack:
            self._handle_error("'si' sans 'alors'", t.line, t.col)
        for t in repeter_stack:
            self._handle_error("'repeter' sans 'jusqua'", t.line, t.col)

    def get_result(self) -> ScanResult:
        self._validate_program_structure()

        return ScanResult(
            tokens=[TokenResponse(type=t.type, lexeme=t.lexeme, line=t.line, col=t.col)
                    for t in self.tokens],
            symbol_table={k: SymbolInfo(**v) for k, v in self.symbol_table.items()},
            errors=[ErrorResponse(line=l, col=c, message=m) for l, c, m in self.errors],
            success=len(self.errors) == 0
        )


def scan_source(source_text: str) -> ScanResult:
    scanner = Scanner(source_text)
    scanner.tokenize()
    return scanner.get_result()
