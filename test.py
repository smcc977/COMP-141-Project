"""
COMP 141: Course Project
Phase 2.1: Parser for Lexp

This program integrates a scanner (Phase 1.1) and a parser for Lexp.
It reads an input file (with a single expression), tokenizes it, and then parses
the tokens to build an abstract syntax tree (AST). The tokens and AST are printed
to the output file.
"""

import sys
import re


token_re = re.compile(r"""
    (?P<KEYWORD>\b(?:if|then|else|endif|while|do|endwhile|skip)\b) |
    (?P<IDENTIFIER>[a-zA-Z][a-zA-Z0-9]*) |
    (?P<NUMBER>\d+) |
    (?P<SYMBOL>[+\-*/();])
    """, re.VERBOSE)

whitespace_re = re.compile(r"\s+")

def parseLine(line):
    tokenList = []
    pos = 0
    while pos < len(line):
        m_ws = whitespace_re.match(line, pos)
        if m_ws:
            pos = m_ws.end()
            if pos >= len(line):
                break
        m = token_re.match(line, pos)
        if m:
            tokenType = m.lastgroup
            tokenValue = m.group(tokenType)
            tokenList.append((tokenValue, tokenType.upper()))
            pos = m.end()
        else:
            tokenList.append((line[pos], "ERROR READING"))
            break
    return tokenList


class ASTNode:
    def __init__(self, token, children=None):
        # token is a tuple (value, type)
        self.token = token
        self.children = children if children is not None else []

def print_ast(node, indent=""):
    """Preorder traversal printing of the AST with indentation."""
    if node is None:
        return
    # Print current node: value and token type.
    print(f"{indent}{node.token[0]} : {node.token[1]}")
    for child in node.children:
        print_ast(child, indent + "  ")

class TokenStream:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def next(self):
        token = self.peek()
        self.pos += 1
        return token

    def expect(self, expected_value=None, expected_type=None):
        token = self.peek()
        if token is None:
            raise Exception("Unexpected end of token stream.")
        val, typ = token
        if expected_value is not None and val != expected_value:
            raise Exception(f"Expected token '{expected_value}', but got '{val}'.")
        if expected_type is not None and typ != expected_type:
            raise Exception(f"Expected token type '{expected_type}', but got '{typ}'.")
        return self.next()


def parse_expression(ts):
    # expression ::= term { + term }
    node = parse_term(ts)
    while True:
        token = ts.peek()
        if token is not None and token[0] == '+':
            op = ts.next()  # Consume '+'
            right = parse_term(ts)
            node = ASTNode(op, children=[node, right])
        else:
            break
    return node

def parse_term(ts):
    # term ::= factor { - factor }
    node = parse_factor(ts)
    while True:
        token = ts.peek()
        if token is not None and token[0] == '-':
            op = ts.next()  # Consume '-'
            right = parse_factor(ts)
            node = ASTNode(op, children=[node, right])
        else:
            break
    return node

def parse_factor(ts):
    # factor ::= piece { / piece }
    node = parse_piece(ts)
    while True:
        token = ts.peek()
        if token is not None and token[0] == '/':
            op = ts.next()  # Consume '/'
            right = parse_piece(ts)
            node = ASTNode(op, children=[node, right])
        else:
            break
    return node

def parse_piece(ts):
    # piece ::= element { * element }
    node = parse_element(ts)
    while True:
        token = ts.peek()
        if token is not None and token[0] == '*':
            op = ts.next()  # Consume '*'
            right = parse_element(ts)
            node = ASTNode(op, children=[node, right])
        else:
            break
    return node

def parse_element(ts):
    # element ::= ( expression ) | NUMBER | IDENTIFIER
    token = ts.peek()
    if token is None:
        raise Exception("Unexpected end of input while parsing element.")
    
    if token[0] == '(':
        ts.next()  # Consume '('
        node = parse_expression(ts)
        # Expect closing parenthesis
        if ts.peek() is None or ts.peek()[0] != ')':
            raise Exception("Missing closing parenthesis.")
        ts.next()  # Consume ')'
        return node
    elif token[1] == "NUMBER" or token[1] == "IDENTIFIER":
        return ASTNode(ts.next())  # Return leaf node.
    else:
        raise Exception(f"Unexpected token {token} in element.")

def parse_tokens(tokens):
    """
    Parse the entire token list and return the AST.
    The token list is wrapped into a TokenStream.
    """
    ts = TokenStream(tokens)
    ast = parse_expression(ts)
    # Check for any leftover tokens.
    if ts.peek() is not None:
        raise Exception(f"Extra token '{ts.peek()}' found after parsing complete expression.")
    return ast

# ------------------------
# Main test driver
# ------------------------

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python parser.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # We will collect tokens from all lines.
    all_tokens = []
    output_lines = []  # To store output for file writing

    try:
        with open(input_file, 'r') as i:
            for line in i:
                line = line.rstrip("\n")
                output_lines.append("Line: " + line)
                tokens = parseLine(line)
                # Check for scanning errors.
                for token in tokens:
                    if token[1] == "ERROR READING":
                        output_lines.append(f"Error: could not read token '{token[0]}' in line: {line}")
                        raise Exception("Scanning error encountered.")
                    output_lines.append(f"{token[0]} : {token[1]}")
                output_lines.append("")  # Blank line between input lines.
                all_tokens.extend(tokens)
        
        # Print tokens section header.
        output_lines.insert(0, "Tokens:")

        # Parse tokens to generate the AST.
        ast = parse_tokens(all_tokens)

        # Print the AST.
        output_lines.append("AST:")
        # We will capture the AST printing in a temporary list of strings.
        def collect_ast(node, indent=""):
            lines = []
            lines.append(f"{indent}{node.token[0]} : {node.token[1]}")
            for child in node.children:
                lines.extend(collect_ast(child, indent + "  "))
            return lines

        ast_lines = collect_ast(ast)
        output_lines.extend(ast_lines)

    except Exception as e:
        output_lines.append("Error: " + str(e))

    # Write the output to file.
    with open(output_file, 'w') as o:
        for line in output_lines:
            o.write(line + "\n")
