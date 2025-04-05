"""
COMP 141: Course Project
Phase 3.1: Evaluator for Lexp

This program integrates a scanner (Phase 1.2) and a parser for Lexp.
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
    (?P<SYMBOL>(:=|[+\-*/();]))
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
        self.token = token
        self.children = children if children is not None else []

def print_ast(node, indent=""):
    if node is None:
        return
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

def parse_expression(ts: TokenStream):
    node = parse_term(ts)
    while True:
        token = ts.peek()
        if token is not None and token[0] == '+':
            op = ts.next()
            right = parse_term(ts)
            node = ASTNode(op, children=[node, right])
        else:
            break
    return node

def parse_term(ts: TokenStream):
    node = parse_factor(ts)
    while True:
        token = ts.peek()
        if token is not None and token[0] == '-':
            op = ts.next()
            right = parse_factor(ts)
            node = ASTNode(op, children=[node, right])
        else:
            break
    return node

def parse_factor(ts: TokenStream):
    node = parse_piece(ts)
    while True:
        token = ts.peek()
        if token is not None and token[0] == '/':
            op = ts.next()
            right = parse_piece(ts)
            node = ASTNode(op, children=[node, right])
        else:
            break
    return node

def parse_piece(ts: TokenStream):
    node = parse_element(ts)
    while True:
        token = ts.peek()
        if token is not None and token[0] == '*':
            op = ts.next()
            right = parse_element(ts)
            node = ASTNode(op, children=[node, right])
        else:
            break
    return node

def parse_element(ts: TokenStream):
    token = ts.peek()
    if token is None:
        raise Exception("Unexpected end of input while parsing element.")
    if token[0] == '(':
        ts.next()
        node = parse_expression(ts)
        if ts.peek() is None or ts.peek()[0] != ')':
            raise Exception("Missing closing parenthesis.")
        ts.next()
        return node
    elif token[1] == "NUMBER" or token[1] == "IDENTIFIER":
        return ASTNode(ts.next())
    else:
        raise Exception(f"Unexpected token {token} in element.")

def parse_statement(ts: TokenStream):
    node = parse_basestatement(ts)
    while True:
        token = ts.peek()
        if token is not None and token[0] == ';':
            semicolon = ts.next()
            right = parse_basestatement(ts)
            node = ASTNode(semicolon, children=[node, right])
        else:
            break
    return node

def parse_basestatement(ts: TokenStream):
    token = ts.peek()
    if token is None:
        raise Exception("Unexpected end of input while parsing basestatement.")
    if token[1] == "KEYWORD":
        if token[0] == "if":
            return parse_ifstatement(ts)
        elif token[0] == "while":
            return parse_whilestatement(ts)
        elif token[0] == "skip":
            return ASTNode(ts.next())
        else:
            raise Exception(f"Unexpected keyword '{token[0]}' in basestatement.")
    elif token[1] == "IDENTIFIER":
        return parse_assignment(ts)
    else:
        raise Exception(f"Unexpected token {token} in basestatement.")

def parse_assignment(ts: TokenStream):
    ident = ts.expect(expected_type="IDENTIFIER")
    op = ts.expect(expected_value=":=", expected_type="SYMBOL")
    expr = parse_expression(ts)
    return ASTNode(op, children=[ASTNode(ident), expr])

def parse_ifstatement(ts: TokenStream):
    ts.expect(expected_value="if", expected_type="KEYWORD")
    condition = parse_expression(ts)
    ts.expect(expected_value="then", expected_type="KEYWORD")
    then_stmt = parse_statement(ts)
    ts.expect(expected_value="else", expected_type="KEYWORD")
    else_stmt = parse_statement(ts)
    ts.expect(expected_value="endif", expected_type="KEYWORD")
    return ASTNode(("IF-STATEMENT", "KEYWORD"), children=[condition, then_stmt, else_stmt])

def parse_whilestatement(ts: TokenStream):
    ts.expect(expected_value="while", expected_type="KEYWORD")
    condition = parse_expression(ts)
    ts.expect(expected_value="do", expected_type="KEYWORD")
    body = parse_statement(ts)
    ts.expect(expected_value="endwhile", expected_type="KEYWORD")
    return ASTNode(("WHILE-LOOP", "KEYWORD"), children=[condition, body])

def parse_tokens(tokens):
    ts = TokenStream(tokens)
    ast = parse_statement(ts)
    if ts.peek() is not None:
        raise Exception(f"Extra token '{ts.peek()}' found after complete parsing.")
    return ast

def collect_ast(node, indent=""):
            lines = []
            lines.append(f"{indent}{node.token[0]} : {node.token[1]}")
            for child in node.children:
                lines.extend(collect_ast(child, indent + "  "))
            return lines

def isValidExpression(stack):
    return len(stack) >= 3 and stack[len(stack) - 1].token[1] == "NUMBER" and stack[len(stack) - 2].token[1] == "NUMBER" and stack[len(stack) - 3].token[1] == "SYMBOL"

def push(node, stack = [], validCount):
    stack.append(node)
    top = len(stack) - 1
    if isValidExpression(stack):
        return stack
    for child in node.children:
        push(child, stack)
    return stack

def evaluate(ast):
    stack = push(ast)
    top = len(stack) - 1
    

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python parser.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    all_tokens = []
    output_lines = []

    try:
        with open(input_file, 'r') as i:
            for line in i:
                line = line.rstrip("\n")
                tokens = parseLine(line)
                if tokens == []:
                    continue
                output_lines.append("Line: " + line)
                for token in tokens:
                    if token[1] == "ERROR READING":
                        output_lines.append(f"Error: could not read token '{token[0]}' in line: {line}")
                        raise Exception("Scanning error encountered.")
                    output_lines.append(f"{token[0]} : {token[1]}")
                output_lines.append("")
                all_tokens.extend(tokens)
        
        output_lines.insert(0, "Tokens:")
        ast = parse_tokens(all_tokens)

        output_lines.append("AST:")
        ast_lines = collect_ast(ast)
        output_lines.extend(ast_lines)

    except Exception as e:
        output_lines.append("Error: " + str(e))

    with open(output_file, 'w') as o:
        for line in output_lines:
            o.write(line + "\n")
    evaluate(ast)