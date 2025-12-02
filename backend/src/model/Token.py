from dataclasses import dataclass
from pydantic import BaseModel
from typing import List, Dict


@dataclass
class Token:
    type: str
    lexeme: str
    line: int
    col: int

class ScanRequest(BaseModel):
    code: str

class TokenResponse(BaseModel):
    type: str
    lexeme: str
    line: int
    col: int

class SymbolInfo(BaseModel):
    first_line: int
    first_col: int
    occurrences: int

class ErrorResponse(BaseModel):
    line: int
    col: int
    message: str

class ScanResult(BaseModel):
    tokens: List[TokenResponse]
    symbol_table: Dict[str, SymbolInfo]
    errors: List[ErrorResponse]
    success: bool