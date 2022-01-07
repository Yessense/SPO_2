import re
import typing as tp

# name : pattern
from regex import regex

from ebnf_parser.lexer.utils import TokenType, Token
from ebnf_parser.parser.utils import Rule, Alternation, Concatenation, Grouping, Repetition, Optional


class RegexGrammar:
    def __init__(self, grammar: tp.List[Rule]):
        self.grammar = grammar
        self.rule_dict: tp.Dict[str, str] = {}
        self.regex_dict: tp.Dict[str, str] = {}
        self.name = ''
        for _ in range(len(self.grammar)):
            for rule in self.grammar:
                # try:
                    self.name = rule.left.name
                    self.transform_rule_to_regex(rule)
                # except:
                #     continue
        for name, pattern in self.rule_dict.items():
            r = regex.compile(pattern)
            self.regex_dict[name] = r







    def process_statement(self, stmnt: tp.Union[Alternation, Concatenation, Repetition, Optional, Rule]) -> str:
        if isinstance(stmnt, Alternation):
            return self.transform_alternation_to_regex(stmnt)
        elif isinstance(stmnt, Rule):
            return self.transform_rule_to_regex(stmnt)
        elif isinstance(stmnt, Concatenation):
            return self.transform_concatenation_to_regex(stmnt)
        elif isinstance(stmnt, Repetition):
            return self.transform_repetition_to_regex(stmnt)
        elif isinstance(stmnt, Optional):
            return self.transform_optional_to_regex(stmnt)
        elif isinstance(stmnt, Grouping):
            return self.transform_grouping_to_regex(stmnt)
        elif isinstance(stmnt, Token):
            if stmnt.tag is TokenType.RULE:
                if stmnt.name in self.rule_dict:
                    return self.rule_dict[stmnt.name]
                elif stmnt.name == self.name:
                    return '(?R)'
                else:
                    raise KeyError(f'{stmnt.name} is not in dict yet')
            elif stmnt.tag is TokenType.LITERAL:
                return re.escape(stmnt.name)

    def transform_alternation_to_regex(self, alternation: Alternation):
        pattern = self.process_statement(alternation.left) + '|'
        statement = self.process_statement(alternation.right)
        pattern += f'({statement})' if len(statement) > 1 else statement
        return pattern

    def transform_concatenation_to_regex(self, concatenation: Concatenation):
        pattern = self.process_statement(concatenation.left)
        pattern += self.process_statement(concatenation.right)
        return pattern

    def transform_repetition_to_regex(self, repetition: Repetition):
        pattern = '(' + self.process_statement(repetition.token) + ')*'
        return pattern

    def transform_rule_to_regex(self, rule: Rule) -> str:
        name: str = rule.left.name
        pattern: str = ''

        if name in self.rule_dict:
            return self.rule_dict[name]
        else:
            pattern += self.process_statement(rule.right)
        self.rule_dict[name] = pattern
        return pattern

    def transform_optional_to_regex(self, optional: Optional):
        pattern = f'({self.process_statement(optional.token)})?'
        return pattern

    def transform_grouping_to_regex(self, grouping: Grouping):
        pattern = f'({self.process_statement(grouping.token)})?'
        return pattern
