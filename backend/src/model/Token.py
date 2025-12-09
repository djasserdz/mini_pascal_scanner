from pydantic import BaseModel
from typing import List, Dict


# =========================================================
# ✅ INTERNAL TOKEN CLASS (USED BY THE SCANNER INTERNALLY)
# =========================================================
class Token:
    def __init__(self, typ: str, lexeme: str, line: int, col: int):
        self.type = typ
        self.lexeme = lexeme
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.lexeme!r}, {self.line}:{self.col})"


# =========================================================
# ✅ API / FASTAPI RESPONSE MODELS (PYDANTIC)
# =========================================================

class ErrorResponse(BaseModel):
    line: int
    col: int
    message: str


class SymbolInfo(BaseModel):
    first_line: int
    first_col: int
    occurrences: int


class TokenResponse(BaseModel):
    type: str
    lexeme: str
    line: int
    col: int


class ScanResult(BaseModel):
    tokens: List[TokenResponse]
    symbol_table: Dict[str, SymbolInfo]
    errors: List[ErrorResponse]
    success: bool

class Request(BaseModel):
    code : str
