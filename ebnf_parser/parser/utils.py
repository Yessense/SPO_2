from enum import Enum

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
    def __init__(self, token: Statement):
        super().__init__()
        self.token = token

    def __str__(self):
        return f'Optional({self.token})'


class Repetition(Statement):
    def __init__(self, token: Statement):
        super().__init__()
        self.token = token

    def __str__(self):
        return f'Repetition({self.token})'


class Grouping(Statement):
    def __init__(self, token: Statement):
        super().__init__()
        self.token = token

    def __str__(self):
        return f'Grouping({self.token})'


class Alternation(Statement):
    def __init__(self, lhs: Statement, rhs: Statement):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return f'Alternation({self.lhs}, {self.rhs})'


class Concatenation(Statement):
    def __init__(self, lhs: Statement, rhs: Statement):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return f'Concatenation({self.lhs}, {self.rhs})'


class Rule(Statement):
    def __init__(self, rule: Statement, stmt: Statement, *args, **kwargs):
        self.rule = rule
        self.stmt = stmt

    def __str__(self):
        return f'Rule({self.rule} = {self.stmt})'
