# mini_pascal_scanner

A simple **tokenizer (lexical scanner)** for a mini Pascal-like language.  
It reads source code as input and converts it into a stream of tokens that can be used by a parser or compiler.

---

## What It Does

The scanner takes raw source code and breaks it into tokens such as:

- Keywords  
- Identifiers  
- Numbers  
- Operators  
- Symbols  
- Delimiters  

Example:

```pascal
var x := 10;
