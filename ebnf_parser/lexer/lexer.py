from .utils import *
import typing as tp


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.current = Character(' ')
        self.index = -1
        self.line = 1
        self.column = 1

    def next_char(self):
        try:
            self.current = Character(self.source[self.index + 1])
            self.index = self.index + 1
            self.column = self.column + 1
        except IndexError:
            self.current = Character('\0')
        return self

    def skip_whitespace(self):
        while self.current.is_space:
            if self.current.is_a('\n'):
                self.line = self.line + 1
                self.column = 0
            self.next_char()
        return self

    def read_literal(self) -> Token:
        quotation = self.current
        word = []

        while True:
            self.next_char()

            # processing 2 symbols literals
            if self.current.is_a('\\'):
                self.next_char()
                if self.current.is_a('t'):
                    ch = '\t'
                elif self.current.is_a('r'):
                    ch = '\r'
                elif self.current.is_a('n'):
                    ch = '\n'
                else:
                    ch = self.current.ch
                word.append(ch)
                self.next_char()

            if self.current == quotation:
                self.next_char()
                break

            if self.current.is_EOF:
                raise RuntimeError("Unexpect end of file")

            word.append(self.current.ch)

        token = Token("".join(word), TokenType.LITERAL)
        return token

    def read_rule(self) -> Token:
        word = []

        while self.current.is_letter or \
                self.current.is_decimal or \
                self.current.is_a('_'):
            word.append(self.current.ch)
            self.next_char()

        return Token("".join(word), TokenType.RULE)

    def read_symbol(self) -> Token:
        token = Token(self.current.ch, TokenType.SYMBOL)
        self.current = Character(' ')
        return token

    def scan(self) -> tp.Optional[Token]:
        self.skip_whitespace()
        # EOF
        if self.current.is_EOF:
            self.current = Character(' ')
            return None
        # Literal
        elif self.current.is_a('"') or self.current.is_a("'"):
            return self.read_literal()
        # Rule
        elif self.current.is_letter:
            return self.read_rule()
        # Symbol
        else:
            return self.read_symbol()

    def scan_all(self):
        tokens = []
        while True:
            token = self.scan()
            if token is None:
                break
            tokens.append(token)
        return tokens
