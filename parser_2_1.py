r'''COMP 141: Course Project
Phase 2.1
Parser for Lexp

Nicholas Henricksen and Samuel McCollough

Code Description:
This program will take an input file and output a text file containing the tokens identified.

The input and output files are specified in the command line.
Please see README.md for instructions on how to use the program.

Grammar
expression ::= term { + term }
term ::= factor { - factor }
factor ::= piece { / piece }
piece ::= element { * element }
element ::= ( expression ) | NUMBER | IDENTIFIER
'''

import sys
import nltk
from nltk import CFG, ChartParser, EarleyChartParser
from scanner_1_1 import parseLine

grammar = CFG.fromstring("""
expression   -> term expression_tail
expression_tail -> '+' term expression_tail | ""
term         -> factor term_tail
term_tail    -> '-' factor term_tail | ""
factor       -> piece factor_tail
factor_tail  -> '/' piece factor_tail | ""
piece        -> element piece_tail
piece_tail   -> '*' element piece_tail | ""
element      -> '(' expression ')' | 'NUMBER' | 'IDENTIFIER'
""")

def convert_tokens(tokens):
    new_tokens = []
    for i in range(len(tokens)):
        if tokens[i][1].lower() == 'identifier':
            new_tokens.append("IDENTIFIER")
        elif tokens[i][1].lower() == 'number':
            new_tokens.append("NUMBER")
        elif tokens[i][1].lower() == 'symbol':
            new_tokens.append(tokens[i][0])
        elif tokens[i][1].lower() == 'keyword':
            print("that is bad")
            return None
    return new_tokens

def match_tokens_to_grammar(tokens):
    parser = EarleyChartParser(grammar)
    parseTree = list(parser.parse(tokens))
    return parseTree

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    with open(input_file, 'r') as i, open(output_file, 'w') as o:
        for line in i:
            line = line.rstrip("\n")
            o.write("Line: " + line + "\n")
            tokens = parseLine(line)
            cfg_tokens = convert_tokens(tokens)
            print(cfg_tokens)
            parse_tree = match_tokens_to_grammar(cfg_tokens)
            if parse_tree:
                print("The token list is valid according to the grammar!")
                for tree in parse_tree:
                    print(tree)
            print(parse_tree)

