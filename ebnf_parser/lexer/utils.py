import dataclasses
from enum import Enum


class Character:
    def __init__(self, ch):
        self.ch = ch

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.ch == other.ch

    def is_a(self, c):
        return self.ch == c

    @property
    def is_EOF(self):
        return self.ch == '\0'

    @property
    def is_letter(self):
        return 'A' <= self.ch <= 'Z' or 'a' <= self.ch <= 'z'

    @property
    def is_decimal(self):
        return '0' <= self.ch <= '9'

    @property
    def is_octal(self):
        return '0' <= self.ch <= '7'

    @property
    def is_hex(self):
        # hexDigit = "0" .. "9" | "A" .. "F" | "a" .. "f"
        return '0' <= self.ch <= '9' or 'A' <= self.ch <= 'F' or 'a' <= self.ch <= 'f'

    @property
    def is_space(self):
        # Whitespace = " " | "\t" | "\r" | "\n"
        return self.ch == ' ' or self.ch == '\t' or \
               self.ch == '\r' or self.ch == '\n'


class TokenType(Enum):
    RULE = 1
    LITERAL = 2
    SYMBOL = 3


@dataclasses.dataclass
class Token:
    token: str
    tag: TokenType

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.token == other.token and self.tag == other.tag

    def __str__(self):
        return f'<{self.token}:{self.tag.name}>'
