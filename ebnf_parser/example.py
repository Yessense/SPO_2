from ebnf_parser.lexer.lexer import Lexer
from ebnf_parser.parser.parser import Parser

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
    print("Done")
