from enum import Enum
import typing as tp

from ebnf_parser.lexer.utils import Token, TokenType


class ParserToken(Enum):
    EQUALS = Token('=', TokenType.SYMBOL)
    SEMICOLON = Token(';', TokenType.SYMBOL)


class Statement:
    def __str__(self):
        return f'stmnt'

    def __repr__(self):
        return self.__str__()


class Optional(Statement):
    def __init__(self, token: Token):
        super().__init__()
        self.token = token

    def __str__(self):
        return f'Optional({self.token})'


class Repetition(Statement):
    def __init__(self, token: tp.Union[Token, Statement]):
        super().__init__()
        self.token = token

    def __str__(self):
        return f'Repetition({self.token})'


class Grouping(Statement):
    def __init__(self, token: Token):
        super().__init__()
        self.token = token

    def __str__(self):
        return f'Grouping({self.token})'


class Alternation(Statement):
    def __init__(self, left: Token, right: tp.Union[Token, Statement]):
        super().__init__()
        self.left = left
        self.right = right

    def __str__(self):
        return f'Alternation({self.left}, {self.right})'


class Concatenation(Statement):
    def __init__(self, left: Token, right: Token):
        super().__init__()
        self.left = left
        self.right = right

    def __str__(self):
        return f'Concatenation({self.left}, {self.right})'


class Rule(Statement):
    def __init__(self, rule: Token, stmt: tp.Union[Statement, Token], *args, **kwargs):
        self.left = rule
        self.right = stmt

    def __str__(self):
        return f'Rule({self.left} = {self.right})'
