from typing import List, Dict, Tuple
from src.model.Token import Token,ScanResult,ErrorResponse,SymbolInfo,TokenResponse
import src.automata as automata



class Scanner:
    def __init__(self, source_text: str, filename: str = "<input>"):
        self.source_original = source_text
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

    def _peek(self, offset: int = 0) -> str:
        p = self.pos + offset
        if p < self.length:
            return self.src[p]
        return ''

    def _skip_whitespace(self):
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
        t = Token(typ, lexeme, line, col)
        self.tokens.append(t)
        self._record_symbol(t)

    def _handle_error(self, message: str, line: int, col: int):
        self.errors.append((line, col, message))

    def tokenize(self):
        """Tokenize the source code"""
        while self.pos < self.length:
            self._skip_whitespace()
            if self.pos >= self.length:
                break

            start_pos = self.pos
            start_line = self.line
            start_col = self.col

            match = self.automaton.match(self.src, self.pos)
            if match is None:
                ch = self.src[self.pos]
                self._handle_error(f"Illegal character: {repr(ch)}", self.line, self.col)
                self._advance(1)
                continue

            typ, lexeme, length = match
            self._add_token(typ, lexeme, start_line, start_col)
            self._advance(length)

        self._add_token("EOF", "", self.line, self.col)

    def get_result(self) -> ScanResult:
        """Return scan results as a Pydantic model for FastAPI"""
        return ScanResult(
            tokens=[
                TokenResponse(
                    type=t.type,
                    lexeme=t.lexeme,
                    line=t.line,
                    col=t.col
                ) for t in self.tokens
            ],
            symbol_table={
                lexeme: SymbolInfo(
                    first_line=info["first_line"],
                    first_col=info["first_col"],
                    occurrences=info["occurrences"]
                ) for lexeme, info in self.symbol_table.items()
            },
            errors=[
                ErrorResponse(line=line, col=col, message=msg)
                for line, col, msg in self.errors
            ],
            success=len(self.errors) == 0
        )

    def get_tokens_text(self) -> str:
        """Get tokens as formatted text (for file download)"""
        lines = []
        for t in self.tokens:
            lex = t.lexeme.replace("\n", "\\n").replace("\r", "\\r")
            lines.append(f"{t.type}\t{lex}\t{t.line}:{t.col}")
        return "\n".join(lines)


def scan_source(source_text: str) -> ScanResult:
    """Scan source code and return results"""
    scanner = Scanner(source_text)
    scanner.tokenize()
    return scanner.get_result()


