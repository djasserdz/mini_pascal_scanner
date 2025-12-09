from typing import Optional, Tuple

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

        # ✅ NUMBERS
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

        # ✅ MULTI OPERATORS
        if pos + 1 < len(src):
            two = src[pos:pos + 2]
            if two in self.multi_ops:
                return (self.multi_ops[two], two, 2)

        # ✅ PUNCTUATION
        if ch in self.punct:
            return (self.punct[ch], ch, 1)

        # ✅ SINGLE OPERATORS
        if ch in self.single_ops:
            return (self.single_ops[ch], ch, 1)

        return None
