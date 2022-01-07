import regex

from ebnf_parser.lexer.lexer import Lexer
from ebnf_parser.parser.parser import Parser
from ebnf_parser.regex_grammar.regex_grammar import RegexGrammar

if __name__ == '__main__':
    ebnf_path = 'ebnf_wiki.txt'
    source = open(ebnf_path, 'r').read()

    lexer = Lexer(source)
    parser = Parser(lexer)
    ebnf_grammar = parser.grammar()

    pascal_path = 'pascal_wiki.txt'
    source = open(pascal_path, 'r').read()

    lexer = Lexer(source)
    parser = Parser(lexer)
    pascal_grammar = parser.grammar()

    regex_grammar = RegexGrammar(grammar=pascal_grammar)
    pattern = regex_grammar.regex_dict['program']
    program_path = 'pascal_program.txt'
    program = open(program_path, 'r').read()
    match = regex.match(pattern, program)
    if match is None:
        print("Program is not correct")
    else:
        print("Program is correct")

    print("Done")
