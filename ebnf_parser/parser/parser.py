from ebnf_parser.lexer.lexer import Lexer
from ebnf_parser.parser.utils import *
import typing as tp


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.look = None
        self.move_next()

    def move_next(self):
        self.look = self.lexer.scan()
        print(self.look)
        return self

    def grammar(self):
        seq = []

        while True:
            rule = self.rule()
            if rule is None:
                break
            seq.append(rule)

        return seq

    def rule(self):
        if self.look is None:
            return None

        rule = self.left()
        self.match(ParserToken.EQUALS.value)
        definition = self.right()
        self.match(ParserToken.SEMICOLON.value)

        return Rule(rule, definition)

    def left(self) -> Rule:
        if self.look.tag == TokenType.RULE:
            token = self.look
            self.move_next()
            return token
        raise TypeError(f"Unexpect {self.look}")

    def right(self) -> tp.Optional[tp.Union[Optional, Repetition, Grouping, Alternation, Concatenation]]:
        token = None
        bracket = None

        # End of parse ';'
        if self.look == ParserToken.SEMICOLON:
            return None

        if self.look.tag in [TokenType.RULE, TokenType.LITERAL]:
            token = self.look
        # Optional statement
        if self.look == Token('[', TokenType.SYMBOL):
            bracket = Token(']', TokenType.SYMBOL)
            self.move_next()
            token = Optional(self.right())
        # Repetition statement
        elif self.look == Token('{', TokenType.SYMBOL):
            bracket = Token('}', TokenType.SYMBOL)
            self.move_next()
            token = Repetition(self.right())
        # Grouping statement
        elif self.look == Token('(', TokenType.SYMBOL):
            bracket = Token(')', TokenType.SYMBOL)
            self.move_next()
            token = Grouping(self.right())
        # Closing bracket
        if bracket is not None:
            if self.look != bracket:
                raise TypeError("Unclosed parentheses")
        self.move_next()

        if self.look == Token('|', TokenType.SYMBOL):
            self.move_next()
            return Alternation(token, self.right())

        if self.look == Token(',', TokenType.SYMBOL):
            self.move_next()
            return Concatenation(token, self.right())

        return token

    def match(self, token):
        if self.look == token:
            return self.move_next()
        raise TypeError(f"Unexpect {self.look}")