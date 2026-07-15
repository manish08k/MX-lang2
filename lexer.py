"""
MX Language Lexer
Tokenizes MX source code into a stream of tokens.
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class TokenType(Enum):
    # Literals
    INT_LIT    = auto()
    FLOAT_LIT  = auto()
    STRING_LIT = auto()
    BOOL_LIT   = auto()
    NULL       = auto()

    # Identifiers & Keywords
    IDENT      = auto()
    LET        = auto()
    CONST      = auto()
    FN         = auto()
    RETURN     = auto()
    IF         = auto()
    ELSE       = auto()
    WHILE      = auto()
    FOR        = auto()
    IN         = auto()
    BREAK      = auto()
    CONTINUE   = auto()
    IMPORT     = auto()
    STRUCT     = auto()
    NEW        = auto()

    # Types
    TYPE_INT   = auto()
    TYPE_FLOAT = auto()
    TYPE_STR   = auto()
    TYPE_BOOL  = auto()
    TYPE_VOID  = auto()

    # Operators
    PLUS       = auto()
    MINUS      = auto()
    STAR       = auto()
    SLASH      = auto()
    PERCENT    = auto()
    POWER      = auto()

    EQ         = auto()   # ==
    NEQ        = auto()   # !=
    LT         = auto()   # <
    GT         = auto()   # >
    LTE        = auto()   # <=
    GTE        = auto()   # >=

    ASSIGN     = auto()   # =
    PLUS_EQ    = auto()   # +=
    MINUS_EQ   = auto()   # -=
    STAR_EQ    = auto()   # *=
    SLASH_EQ   = auto()   # /=

    AND        = auto()   # and / &&
    OR         = auto()   # or  / ||
    NOT        = auto()   # not / !

    # Delimiters
    LPAREN     = auto()   # (
    RPAREN     = auto()   # )
    LBRACE     = auto()   # {
    RBRACE     = auto()   # }
    LBRACKET   = auto()   # [
    RBRACKET   = auto()   # ]

    COMMA      = auto()   # ,
    SEMICOLON  = auto()   # ;
    COLON      = auto()   # :
    DOT        = auto()   # .
    ARROW      = auto()   # ->
    DOTDOT     = auto()   # ..  (range)

    # Special
    EOF        = auto()
    NEWLINE    = auto()


KEYWORDS = {
    'let':      TokenType.LET,
    'const':    TokenType.CONST,
    'fn':       TokenType.FN,
    'return':   TokenType.RETURN,
    'if':       TokenType.IF,
    'else':     TokenType.ELSE,
    'while':    TokenType.WHILE,
    'for':      TokenType.FOR,
    'in':       TokenType.IN,
    'break':    TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'import':   TokenType.IMPORT,
    'struct':   TokenType.STRUCT,
    'new':      TokenType.NEW,
    'true':     TokenType.BOOL_LIT,
    'false':    TokenType.BOOL_LIT,
    'null':     TokenType.NULL,
    'and':      TokenType.AND,
    'or':       TokenType.OR,
    'not':      TokenType.NOT,
    'int':      TokenType.TYPE_INT,
    'float':    TokenType.TYPE_FLOAT,
    'str':      TokenType.TYPE_STR,
    'bool':     TokenType.TYPE_BOOL,
    'void':     TokenType.TYPE_VOID,
}


@dataclass
class Token:
    type: TokenType
    value: object
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col})"


class LexerError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(f"[Lexer Error] Line {line}, Col {col}: {msg}")
        self.line = line
        self.col = col


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: list[Token] = []

    def error(self, msg):
        raise LexerError(msg, self.line, self.col)

    def peek(self, offset=0) -> Optional[str]:
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return None

    def advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def match(self, expected: str) -> bool:
        if self.pos < len(self.source) and self.source[self.pos] == expected:
            self.advance()
            return True
        return False

    def skip_whitespace_and_comments(self):
        while self.pos < len(self.source):
            ch = self.peek()
            if ch in (' ', '\t', '\r'):
                self.advance()
            elif ch == '\n':
                self.advance()
            elif ch == '/' and self.peek(1) == '/':
                # Single-line comment
                while self.pos < len(self.source) and self.peek() != '\n':
                    self.advance()
            elif ch == '/' and self.peek(1) == '*':
                # Multi-line comment
                self.advance(); self.advance()
                while self.pos < len(self.source):
                    if self.peek() == '*' and self.peek(1) == '/':
                        self.advance(); self.advance()
                        break
                    self.advance()
            elif ch == '#':
                # Python-style comment
                while self.pos < len(self.source) and self.peek() != '\n':
                    self.advance()
            else:
                break

    def read_string(self, quote: str) -> Token:
        line, col = self.line, self.col
        result = []
        while self.pos < len(self.source):
            ch = self.peek()
            if ch is None:
                self.error("Unterminated string literal")
            if ch == quote:
                self.advance()
                break
            if ch == '\\':
                self.advance()
                esc = self.advance()
                escape_map = {'n': '\n', 't': '\t', 'r': '\r',
                              '\\': '\\', '"': '"', "'": "'", '0': '\0'}
                result.append(escape_map.get(esc, esc))
            else:
                result.append(self.advance())
        return Token(TokenType.STRING_LIT, ''.join(result), line, col)

    def read_number(self) -> Token:
        line, col = self.line, self.col
        start = self.pos
        is_float = False
        while self.pos < len(self.source) and self.peek().isdigit():
            self.advance()
        if self.peek() == '.' and self.peek(1) and self.peek(1).isdigit():
            is_float = True
            self.advance()
            while self.pos < len(self.source) and self.peek().isdigit():
                self.advance()
        raw = self.source[start:self.pos]
        if is_float:
            return Token(TokenType.FLOAT_LIT, float(raw), line, col)
        return Token(TokenType.INT_LIT, int(raw), line, col)

    def read_ident(self) -> Token:
        line, col = self.line, self.col
        start = self.pos
        while self.pos < len(self.source) and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()
        word = self.source[start:self.pos]
        ttype = KEYWORDS.get(word, TokenType.IDENT)
        value = word
        if ttype == TokenType.BOOL_LIT:
            value = word == 'true'
        return Token(ttype, value, line, col)

    def tokenize(self) -> list[Token]:
        while True:
            self.skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                self.tokens.append(Token(TokenType.EOF, None, self.line, self.col))
                break

            line, col = self.line, self.col
            ch = self.advance()

            # String literals
            if ch in ('"', "'"):
                self.tokens.append(self.read_string(ch))

            # Numbers
            elif ch.isdigit():
                self.pos -= 1; self.col -= 1
                self.tokens.append(self.read_number())

            # Identifiers / Keywords
            elif ch.isalpha() or ch == '_':
                self.pos -= 1; self.col -= 1
                self.tokens.append(self.read_ident())

            # Operators
            elif ch == '+':
                if self.match('='):
                    self.tokens.append(Token(TokenType.PLUS_EQ, '+=', line, col))
                else:
                    self.tokens.append(Token(TokenType.PLUS, '+', line, col))
            elif ch == '-':
                if self.match('>'):
                    self.tokens.append(Token(TokenType.ARROW, '->', line, col))
                elif self.match('='):
                    self.tokens.append(Token(TokenType.MINUS_EQ, '-=', line, col))
                else:
                    self.tokens.append(Token(TokenType.MINUS, '-', line, col))
            elif ch == '*':
                if self.match('*'):
                    self.tokens.append(Token(TokenType.POWER, '**', line, col))
                elif self.match('='):
                    self.tokens.append(Token(TokenType.STAR_EQ, '*=', line, col))
                else:
                    self.tokens.append(Token(TokenType.STAR, '*', line, col))
            elif ch == '/':
                if self.match('='):
                    self.tokens.append(Token(TokenType.SLASH_EQ, '/=', line, col))
                else:
                    self.tokens.append(Token(TokenType.SLASH, '/', line, col))
            elif ch == '%':
                self.tokens.append(Token(TokenType.PERCENT, '%', line, col))
            elif ch == '=':
                if self.match('='):
                    self.tokens.append(Token(TokenType.EQ, '==', line, col))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', line, col))
            elif ch == '!':
                if self.match('='):
                    self.tokens.append(Token(TokenType.NEQ, '!=', line, col))
                else:
                    self.tokens.append(Token(TokenType.NOT, '!', line, col))
            elif ch == '<':
                if self.match('='):
                    self.tokens.append(Token(TokenType.LTE, '<=', line, col))
                else:
                    self.tokens.append(Token(TokenType.LT, '<', line, col))
            elif ch == '>':
                if self.match('='):
                    self.tokens.append(Token(TokenType.GTE, '>=', line, col))
                else:
                    self.tokens.append(Token(TokenType.GT, '>', line, col))
            elif ch == '&' and self.match('&'):
                self.tokens.append(Token(TokenType.AND, '&&', line, col))
            elif ch == '|' and self.match('|'):
                self.tokens.append(Token(TokenType.OR, '||', line, col))

            # Delimiters
            elif ch == '(':  self.tokens.append(Token(TokenType.LPAREN,   '(', line, col))
            elif ch == ')':  self.tokens.append(Token(TokenType.RPAREN,   ')', line, col))
            elif ch == '{':  self.tokens.append(Token(TokenType.LBRACE,   '{', line, col))
            elif ch == '}':  self.tokens.append(Token(TokenType.RBRACE,   '}', line, col))
            elif ch == '[':  self.tokens.append(Token(TokenType.LBRACKET, '[', line, col))
            elif ch == ']':  self.tokens.append(Token(TokenType.RBRACKET, ']', line, col))
            elif ch == ',':  self.tokens.append(Token(TokenType.COMMA,    ',', line, col))
            elif ch == ';':  self.tokens.append(Token(TokenType.SEMICOLON,';', line, col))
            elif ch == ':':  self.tokens.append(Token(TokenType.COLON,    ':', line, col))
            elif ch == '.':
                if self.match('.'):
                    self.tokens.append(Token(TokenType.DOTDOT, '..', line, col))
                else:
                    self.tokens.append(Token(TokenType.DOT, '.', line, col))

            else:
                self.error(f"Unexpected character: {ch!r}")

        return self.tokens
