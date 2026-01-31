#!/usr/bin/env python3
"""
Scanner for MiniPascal-Fr Language
===================================
Usage: python scanner.py [input_file] [output_file]
Default: python scanner.py text.txt tokens.txt

Reads source code from input file and writes tokens to output file.
"""

import sys
from typing import Optional, Tuple, Dict, List

# ══════════════════════════════════════════════════════════════
# AUTOMATON - Lexical Analysis
# ══════════════════════════════════════════════════════════════

KEYWORDS = {
    "programme": "PROGRAMME",
    "constante": "CONSTANTE",
    "variable": "VARIABLE",
    "entier": "ENTIER",
    "reel": "REEL",
    "debut": "DEBUT",
    "fin": "FIN",
    "si": "SI",
    "alors": "ALORS",
    "sinon": "SINON",
    "tantque": "TANTQUE",
    "faire": "FAIRE",
    "repeter": "REPETER",
    "jusqua": "JUSQUA",
    "pour": "POUR",
    "allant": "ALLANT",
    "de": "DE",
    "a": "A",
    "pas": "PAS",
    "ou": "OU",
    "et": "ET",
    "div": "DIV_KEYWORD",
    "mod": "MOD_KEYWORD",
}

PUNCTUATION = {
    ';': 'POINT_VIRGULE',
    ',': 'VIRGULE',
    ':': 'DEUX_POINTS',
    '.': 'POINT',
    '(': 'PARENT_OUV',
    ')': 'PARENT_FERM',
}

SINGLE_OPERATORS = {
    '+': 'PLUS',
    '-': 'MOINS',
    '*': 'FOIS',
    '/': 'DIVISION',
    '<': 'INF',
    '>': 'SUP',
    '=': 'EGAL',
}

MULTI_OPERATORS = {
    ':=': 'AFFECTATION',
    '<=': 'INFEGAL',
    '>=': 'SUPEGAL',
    '<>': 'DIFF',
}


def is_letter(ch: str) -> bool:
    return ('a' <= ch <= 'z') or ('A' <= ch <= 'Z')


def is_digit(ch: str) -> bool:
    return '0' <= ch <= '9'


def is_alnum(ch: str) -> bool:
    return is_letter(ch) or is_digit(ch)


class Automaton:
    def __init__(self):
        self.keywords = KEYWORDS
        self.punct = PUNCTUATION
        self.single_ops = SINGLE_OPERATORS
        self.multi_ops = MULTI_OPERATORS

    def match(self, src: str, pos: int) -> Optional[Tuple[str, str, int]]:
        if pos >= len(src):
            return None

        ch = src[pos]

        # IDENTIFIERS and KEYWORDS
        if is_letter(ch):
            i = pos + 1
            while i < len(src) and is_alnum(src[i]):
                i += 1

            lexeme_raw = src[pos:i]
            lexeme_lower = lexeme_raw.lower()

            if lexeme_lower in self.keywords:
                return (self.keywords[lexeme_lower], lexeme_raw, i - pos)

            # Identifiers: letter, then a digit, then any mix of letters/digits
            if len(lexeme_raw) >= 2 and is_digit(lexeme_raw[1]):
                return ("ID", lexeme_raw, i - pos)

            return None

        # NUMBERS
        if is_digit(ch):
            i = pos
            while i < len(src) and is_digit(src[i]):
                i += 1

            if i < len(src) and src[i] == '.' and i + 1 < len(src) and is_digit(src[i + 1]):
                i += 1
                while i < len(src) and is_digit(src[i]):
                    i += 1
                return ("NOMBRE_REEL", src[pos:i], i - pos)

            return ("NOMBRE_ENTIER", src[pos:i], i - pos)

        # MULTI OPERATORS
        if pos + 1 < len(src):
            two = src[pos:pos + 2]
            if two in self.multi_ops:
                return (self.multi_ops[two], two, 2)

        # PUNCTUATION
        if ch in self.punct:
            return (self.punct[ch], ch, 1)

        # SINGLE OPERATORS
        if ch in self.single_ops:
            return (self.single_ops[ch], ch, 1)

        return None


# ══════════════════════════════════════════════════════════════
# SCANNER
# ══════════════════════════════════════════════════════════════

class Token:
    def __init__(self, type_: str, lexeme: str, line: int, col: int):
        self.type = type_
        self.lexeme = lexeme
        self.line = line
        self.col = col

    def __repr__(self):
        return f"{self.type}({self.lexeme})@{self.line}:{self.col}"


class Scanner:
    def __init__(self, source_text: str):
        self.src = source_text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.automaton = Automaton()
        self.tokens: List[Token] = []
        self.errors: List[str] = []
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

    def _add_token(self, typ: str, lexeme: str, line: int, col: int):
        token = Token(typ, lexeme, line, col)
        self.tokens.append(token)

    def _handle_error(self, message: str, line: int, col: int):
        error_msg = f"[ERREUR_LEXICALE] ligne {line}, col {col}: {message}"
        self.errors.append(error_msg)

    def tokenize(self):
        while self.pos < self.length:
            if self._skip_whitespace():
                continue

            start_line = self.line
            start_col = self.col

            match = self.automaton.match(self.src, self.pos)
            if match is None:
                # Handle invalid identifiers gracefully
                ch = self.src[self.pos]
                if is_letter(ch):
                    i = self.pos + 1
                    while i < self.length and is_alnum(self.src[i]):
                        i += 1
                    lexeme = self.src[self.pos:i]
                    self._handle_error(
                        f"Identificateur invalide (doit être lettre + chiffre ...): {lexeme!r}",
                        self.line,
                        self.col,
                    )
                    self._advance(i - self.pos)
                else:
                    self._handle_error(f"Caractère illégal: {repr(ch)}", self.line, self.col)
                    self._advance(1)
                continue

            typ, lexeme, length = match
            self._add_token(typ, lexeme, start_line, start_col)
            self._advance(length)

        self._add_token("EOF", "", self.line, self.col)


# ══════════════════════════════════════════════════════════════
# MAIN - Command Line Interface
# ══════════════════════════════════════════════════════════════

def main():
    # Parse command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "text.txt"

    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = "tokens.txt"

    # Read source code
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"❌ Erreur: Le fichier '{input_file}' n'existe pas.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de '{input_file}': {e}")
        sys.exit(1)

    # Run scanner
    print("=" * 60)
    print(f"  Scanner - Analyse Lexicale")
    print("=" * 60)
    print(f"  Fichier d'entrée : {input_file}")
    print(f"  Fichier de sortie: {output_file}")
    print("=" * 60)

    scanner = Scanner(source_code)
    scanner.tokenize()

    # Display errors if any
    if scanner.errors:
        print("\n⚠️  Erreurs détectées:")
        print("-" * 60)
        for error in scanner.errors:
            print(f"  {error}")
        print("-" * 60)

    # Write tokens to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for token in scanner.tokens:
                # Format: TYPE LEXEME LINE
                f.write(f"{token.type} {token.lexeme} {token.line}\n")
        
        print(f"\n✅ Analyse lexicale terminée!")
        print(f"   Tokens écrits dans '{output_file}'")
        print(f"   Total: {len(scanner.tokens)} tokens")
        if scanner.errors:
            print(f"   ⚠️  {len(scanner.errors)} erreur(s) détectée(s)")
        else:
            print(f"   ✓  Aucune erreur")
    except Exception as e:
        print(f"❌ Erreur lors de l'écriture de '{output_file}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
