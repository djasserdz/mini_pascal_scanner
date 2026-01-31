#!/usr/bin/env python3
"""
Parser for MiniPascal-Fr Language
==================================
Usage: python parser.py [input_file] [output_file]
Default: python parser.py tokens.txt output.txt

Reads tokens from input file and writes parse results to output file.
"""

import sys
from typing import List

# ══════════════════════════════════════════════════════════════
# TOKEN CLASS
# ══════════════════════════════════════════════════════════════

class Token:
    __slots__ = ("type", "lexeme", "line")

    def __init__(self, type_: str, lexeme: str, line: int):
        self.type = type_          # KEYWORD | ID | NOMBRE | SYMBOLE | EOF
        self.lexeme = lexeme
        self.line = line

    def __repr__(self):
        return f"{self.type}({self.lexeme})@{self.line}"


# ══════════════════════════════════════════════════════════════
# PARSER CLASS
# ══════════════════════════════════════════════════════════════

class Parser:
    # Constants
    KEYWORDS = {
        "programme", "constante", "variable", "entier", "reel",
        "debut", "fin", "si", "alors", "sinon",
        "tantque", "faire", "repeter", "jusqua",
        "pour", "allant", "de", "a", "pas",
        "ou", "et", "div", "mod"
    }

    RELATIONAL_OPS = {"<", ">", "=", "<=", ">=", "<>"}

    def __init__(self):
        self.tokens: List[Token] = []
        self.pos: int = 0
        self.current: Token = None
        self.rules: List[str] = []
        self.errors: List[str] = []

    # ── FILE I/O ───────────────────────────────────────────────

    def load_tokens(self, path: str) -> None:
        """Load tokens from file. Format: TYPE LEXEME LINE"""
        self.tokens = []
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for raw_line in fh:
                    parts = raw_line.split()
                    if len(parts) < 2:
                        continue  # skip blank/malformed
                    
                    typ = parts[0].upper()
                    lexeme = parts[1]
                    line = int(parts[2]) if len(parts) >= 3 else 0
                    
                    # Convert scanner token types to parser token types
                    parser_token = self._convert_token_type(typ, lexeme, line)
                    self.tokens.append(parser_token)
        except FileNotFoundError:
            print(f"❌ Erreur: Le fichier '{path}' n'existe pas.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Erreur lors de la lecture de '{path}': {e}")
            sys.exit(1)

        # Ensure EOF sentinel
        if not self.tokens or self.tokens[-1].type != "EOF":
            self.tokens.append(Token("EOF", "EOF", 0))

    def _convert_token_type(self, scanner_type: str, lexeme: str, line: int) -> Token:
        """Convert scanner token types to parser token types."""
        if scanner_type == "ID":
            return Token("ID", lexeme, line)
        if scanner_type in ("NOMBRE_ENTIER", "NOMBRE_REEL", "NOMBRE"):
            return Token("NOMBRE", lexeme, line)
        if scanner_type == "EOF":
            return Token("EOF", "EOF", line)
        
        # Keywords: detect by lexeme membership in parser's KEYWORDS
        if lexeme.lower() in self.KEYWORDS:
            return Token("KEYWORD", lexeme, line)
        
        # Everything else (punctuation, operators) -> SYMBOLE
        return Token("SYMBOLE", lexeme, line)

    def write_output(self, path: str) -> None:
        """Write parse results to output file."""
        try:
            with open(path, "w", encoding="utf-8") as fh:
                # Write header
                fh.write("=" * 60 + "\n")
                fh.write("  Résultat de l'Analyse Syntaxique\n")
                fh.write("=" * 60 + "\n\n")
                
                # Write rules
                fh.write("-" * 60 + "\n")
                fh.write("  Séquence de Règles Appliquées\n")
                fh.write("-" * 60 + "\n")
                for i, r in enumerate(self.rules, 1):
                    fh.write(f"  {i:>4d} : {r}\n")
                
                # Write errors or success message
                fh.write("\n")
                if self.errors:
                    fh.write("-" * 60 + "\n")
                    fh.write("  Erreurs Détectées\n")
                    fh.write("-" * 60 + "\n")
                    for e in self.errors:
                        fh.write(f"  {e}\n")
                    fh.write("\n")
                    fh.write(f"  ❌ Analyse échouée: {len(self.errors)} erreur(s)\n")
                else:
                    fh.write("  ✅ Analyse syntaxique réussie - aucune erreur.\n")
                
                fh.write("\n" + "=" * 60 + "\n")
        except Exception as e:
            print(f"❌ Erreur lors de l'écriture de '{path}': {e}")
            sys.exit(1)

    # ── LOW-LEVEL HELPERS ──────────────────────────────────────

    def _advance(self) -> None:
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]

    def _match(self, tp: str, lexeme: str) -> bool:
        """Consume current token if it matches (type, lexeme). Case-insensitive on lexeme."""
        if self.current.type == tp and self.current.lexeme.lower() == lexeme.lower():
            self._advance()
            return True
        return False

    def _match_type(self, tp: str) -> bool:
        """Consume current token if its type matches."""
        if self.current.type == tp:
            self._advance()
            return True
        return False

    def _expect(self, tp: str, lexeme: str) -> None:
        """Consume (tp, lexeme) or log error and skip one token (recovery)."""
        if not self._match(tp, lexeme):
            self._error(f"'{lexeme}' attendu, trouvé '{self.current.lexeme}'")
            self._advance()  # skip bad token → try to continue

    def _error(self, message: str) -> None:
        entry = f"[ERREUR_SYNTAXIQUE] ligne {self.current.line} : {message}"
        self.errors.append(entry)

    def _rule(self, text: str) -> None:
        self.rules.append(text)

    # ── PREDICATES (no consumption) ────────────────────────────

    def _is_kw(self, kw: str) -> bool:
        return self.current.type == "KEYWORD" and self.current.lexeme.lower() == kw.lower()

    def _is_sym(self, s: str) -> bool:
        return self.current.type == "SYMBOLE" and self.current.lexeme == s

    def _is_id(self) -> bool:
        return self.current.type == "ID"

    def _is_nombre(self) -> bool:
        return self.current.type == "NOMBRE"

    def _peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def _is_op_rel(self) -> bool:
        return self.current.type == "SYMBOLE" and self.current.lexeme in self.RELATIONAL_OPS

    def _is_op_add(self) -> bool:
        return self._is_sym("+") or self._is_sym("-") or self._is_kw("ou")

    def _is_op_mult(self) -> bool:
        return self._is_sym("*") or self._is_kw("div") or self._is_kw("mod") or self._is_kw("et")

    # ══════════════════════════════════════════════════════════
    # GRAMMAR - one method per non-terminal
    # ══════════════════════════════════════════════════════════

    def _programme_pascal(self) -> None:
        self._rule("ProgrammePascal -> programme NomProgramme ; Corps .")
        self._expect("KEYWORD", "programme")
        self._nom_programme()
        self._expect("SYMBOLE", ";")
        self._corps()
        self._expect("SYMBOLE", ".")

    def _corps(self) -> None:
        self._rule("Corps -> [PartieDéfinitionConstante] [PartieDéfinitionVariable] InstrComp")
        if self._is_kw("constante"):
            self._partie_definition_constante()
        if self._is_kw("variable"):
            self._partie_definition_variable()
        self._instr_comp()

    def _partie_definition_constante(self) -> None:
        self._rule("PartieDéfinitionConstante -> constante DéfinitionConstante {DéfinitionConstante}")
        self._expect("KEYWORD", "constante")
        self._definition_constante()
        while self._is_id():
            self._definition_constante()

    def _definition_constante(self) -> None:
        self._rule("DéfinitionConstante -> NomConstante = Constante ;")
        self._nom_constante()
        self._expect("SYMBOLE", "=")
        self._constante()
        self._expect("SYMBOLE", ";")

    def _partie_definition_variable(self) -> None:
        self._rule("PartieDéfinitionVariable -> variable DéfinitionVariable {DéfinitionVariable}")
        self._expect("KEYWORD", "variable")
        self._definition_variable()
        while self._is_id():
            self._definition_variable()

    def _definition_variable(self) -> None:
        self._rule("DéfinitionVariable -> NomVariable {, NomVariable} : Type ;")
        self._nom_variable()
        while self._is_sym(","):
            self._advance()
            self._nom_variable()
        self._expect("SYMBOLE", ":")
        self._type()
        self._expect("SYMBOLE", ";")

    def _type(self) -> None:
        if self._is_kw("entier"):
            self._rule("Type -> entier")
            self._advance()
        elif self._is_kw("reel"):
            self._rule("Type -> reel")
            self._advance()
        else:
            self._error("type attendu (entier ou reel)")
            self._advance()

    def _nom_programme(self) -> None:
        self._rule("NomProgramme -> ID")
        if not self._match_type("ID"):
            self._error("identificateur attendu pour le nom du programme")

    def _nom_constante(self) -> None:
        self._rule("NomConstante -> ID")
        if not self._match_type("ID"):
            self._error("identificateur attendu pour le nom de constante")

    def _nom_variable(self) -> None:
        self._rule("NomVariable -> ID")
        if not self._match_type("ID"):
            self._error("identificateur attendu pour le nom de variable")

    def _constante(self) -> None:
        if self._is_nombre():
            self._rule(f"Constante -> {self.current.lexeme}")
            self._advance()
        elif self._is_id():
            self._rule(f"Constante -> {self.current.lexeme}")
            self._advance()
        else:
            self._error("constante attendue (nombre ou identificateur)")
            self._advance()

    def _instr_comp(self) -> None:
        self._rule("InstrComp -> debut Instruction { ; Instruction } fin")
        self._expect("KEYWORD", "debut")
        self._instruction()
        while self._is_sym(";"):
            self._advance()
            self._instruction()
        self._expect("KEYWORD", "fin")

    def _instruction(self) -> None:
        if self._is_id():
            self._rule("Instruction -> InstructionAffectation")
            self._instruction_affectation()
        elif self._is_kw("si"):
            self._rule("Instruction -> InstructionSi")
            self._instruction_si()
        elif self._is_kw("tantque"):
            self._rule("Instruction -> InstructionTantque")
            self._instruction_tantque()
        elif self._is_kw("repeter"):
            self._rule("Instruction -> InstructionRepeter")
            self._instruction_repeter()
        elif self._is_kw("debut"):
            self._rule("Instruction -> InstrComp")
            self._instr_comp()
        elif self._is_kw("pour"):
            self._rule("Instruction -> InstructionPour")
            self._instruction_pour()
        else:
            # <Vide> – empty instruction
            self._rule("Instruction -> Vide")

    def _instruction_affectation(self) -> None:
        self._rule("InstructionAffectation -> NomVariable := Expression")
        self._nom_variable()
        self._expect("SYMBOLE", ":=")
        self._expression()

    def _expression(self) -> None:
        self._rule("Expression -> ExpressionSimple [OperateurRelationnel ExpressionSimple]")
        self._expression_simple()
        if self._is_op_rel():
            self._operateur_relationnel()
            self._expression_simple()

    def _operateur_relationnel(self) -> None:
        self._rule(f"OperateurRelationnel -> {self.current.lexeme}")
        self._advance()

    def _expression_simple(self) -> None:
        self._rule("ExpressionSimple -> [OperateurSigne] Terme {OperateurAddition Terme}")
        if self._is_sym("+") or self._is_sym("-"):
            self._rule(f"OperateurSigne -> {self.current.lexeme}")
            self._advance()
        self._terme()
        while self._is_op_add():
            self._operateur_addition()
            self._terme()

    def _operateur_addition(self) -> None:
        self._rule(f"OperateurAddition -> {self.current.lexeme}")
        self._advance()

    def _terme(self) -> None:
        self._rule("Terme -> Facteur {OperateurMult Facteur}")
        self._facteur()
        while self._is_op_mult():
            self._operateur_mult()
            self._facteur()

    def _operateur_mult(self) -> None:
        self._rule(f"OperateurMult -> {self.current.lexeme}")
        self._advance()

    def _facteur(self) -> None:
        if self._is_sym("("):
            self._rule("Facteur -> ( Expression )")
            self._advance()
            self._expression()
            self._expect("SYMBOLE", ")")
        elif self._is_nombre():
            self._rule("Facteur -> Constante")
            self._constante()
        elif self._is_id():
            self._rule("Facteur -> Constante | NomVariable")
            self._constante()
        else:
            self._error(f"facteur attendu (nombre, identifiant ou '('), trouvé '{self.current.lexeme}'")
            self._advance()

    def _instruction_si(self) -> None:
        self._rule("InstructionSi -> si Expression alors Instruction [sinon Instruction]")
        self._expect("KEYWORD", "si")
        self._expression()
        self._expect("KEYWORD", "alors")
        self._instruction()
        if self._is_kw("sinon"):
            self._advance()
            self._instruction()

    def _instruction_tantque(self) -> None:
        self._rule("InstructionTantque -> tantque Expression faire Instruction")
        self._expect("KEYWORD", "tantque")
        self._expression()
        self._expect("KEYWORD", "faire")
        self._instruction()

    def _instruction_repeter(self) -> None:
        self._rule("InstructionRepeter -> repeter Instruction jusqua Expression")
        self._expect("KEYWORD", "repeter")
        self._instruction()
        self._expect("KEYWORD", "jusqua")
        self._expression()

    def _instruction_pour(self) -> None:
        self._rule("InstructionPour -> pour NomVariable allant de Constante a Constante [pas Constante] faire Instruction")
        self._expect("KEYWORD", "pour")
        self._nom_variable()
        self._expect("KEYWORD", "allant")
        self._expect("KEYWORD", "de")
        self._constante()
        self._expect("KEYWORD", "a")
        self._constante()
        if self._is_kw("pas"):
            self._advance()
            self._constante()
        self._expect("KEYWORD", "faire")
        self._instruction()

    # ── PUBLIC INTERFACE ───────────────────────────────────────

    def parse(self):
        """Run the parser on loaded tokens."""
        if not self.tokens:
            print("❌ Aucun token chargé!")
            return False
        
        self.pos = 0
        self.current = self.tokens[0]
        self.rules = []
        self.errors = []

        try:
            self._programme_pascal()
            if self.current.type != "EOF":
                self._error("token inattendu après la fin du programme")
        except Exception as e:
            self._error(f"Exception pendant parsing: {e}")

        return len(self.errors) == 0


# ══════════════════════════════════════════════════════════════
# MAIN - Command Line Interface
# ══════════════════════════════════════════════════════════════

def main():
    # Parse command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "tokens.txt"

    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = "output.txt"

    # Display header
    print("=" * 60)
    print(f"  Parser - Analyse Syntaxique")
    print("=" * 60)
    print(f"  Fichier d'entrée : {input_file}")
    print(f"  Fichier de sortie: {output_file}")
    print("=" * 60)

    # Create parser and load tokens
    parser = Parser()
    parser.load_tokens(input_file)

    print(f"\n✓ {len(parser.tokens)} tokens chargés")
    print("\nDébut de l'analyse syntaxique...\n")

    # Run parser
    success = parser.parse()

    # Display summary on console
    print("\n" + "-" * 60)
    if success:
        print("  ✅ Analyse syntaxique réussie!")
        print(f"     {len(parser.rules)} règles appliquées")
    else:
        print(f"  ❌ Analyse échouée: {len(parser.errors)} erreur(s)")
        print("\n  Erreurs:")
        for error in parser.errors:
            print(f"    {error}")
    print("-" * 60)

    # Write output file
    parser.write_output(output_file)
    print(f"\n✅ Résultats écrits dans '{output_file}'")


if __name__ == "__main__":
    main()
