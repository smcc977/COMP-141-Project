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
from scanner_1_2 import parseLine

token_re = re.compile(r"""
    (?P<KEYWORD>\b(?:if|then|else|endif|while|do|endwhile|skip)\b) |
    (?P<IDENTIFIER>[a-zA-Z][a-zA-Z0-9]*) |
    (?P<NUMBER>\d+) |
    (?P<SYMBOL>:=|[+\-*/();])
    """, re.VERBOSE)

whitespace_re = re.compile(r"\s+")


class ASTNode:
    def __init__(self, token, children=None):
        self.token = token
        self.children = children if children is not None else []


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


def parse_term(ts):
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


def parse_factor(ts):
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


def parse_piece(ts):
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


def parse_element(ts):
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


def parse_tokens(tokens):
    ts = TokenStream(tokens)
    ast = parse_expression(ts)
    if ts.peek() is not None:
        raise Exception(f"Extra token '{ts.peek()}' found after parsing complete expression.")
    return ast


def collect_ast(node, indent=""):
    lines = []
    lines.append(f"{indent}{node.token[0]} : {node.token[1]}")
    for child in node.children:
        lines.extend(collect_ast(child, indent + "  "))
    return lines

def isValidExpression(stack):
    return len(stack) >= 3 and stack[len(stack) - 1].token[1] == "NUMBER" and stack[len(stack) - 2].token[1] == "NUMBER" and stack[len(stack) - 3].token[1] == "SYMBOL"

class LinearAST:
    def __init__(self, ast):
        self.nodes = self.push(ast)
        self.index = self.getIndex()

    def push(self, node, stack = []):
        stack.append(node)
        top = len(stack) - 1
        for child in node.children:
            self.push(child, stack)
        return stack

    def pop(self):
        value = self.nodes[self.index]
        self.index += 1
        return value

    def getIndex(self):
        for i in range(len(self.nodes)):
            if isValidExpression(self.nodes[:i]):
                return i
        return len(self.nodes)

    def getStack(self):
        return self.nodes[:self.index]


def evaluate(ast):
    linear = LinearAST(ast)
    stack = LinearAST(ast).getStack()
    return eval(linear, stack)

def eval(linear, stack):
    if len(stack) == 0:
        raise Exception("Unexpected end of input while evaluating AST.")

    if len(stack) == 1:
        return stack[0]

    if len(stack) == 2:
        raise Exception("Two values left in stack.")

    top = len(stack) - 1
    if isValidExpression(stack):
        symbol = stack[top - 2].token[0]
        if symbol == "+":
            stack.append(ASTNode((str(int(stack[top - 1].token[0]) + int(stack[top].token[0])), "NUMBER"), []))
        elif symbol == "-":
            stack.append(ASTNode((str(int(stack[top -1].token[0]) - int(stack[top].token[0])), "NUMBER"), []))
            if int(stack[len(stack) - 1].token[0]) < 0:
                stack[len(stack) - 1].token = ("0", "NUMBER")
        elif symbol == "*":
            stack.append(ASTNode((str(int(stack[top - 1].token[0]) * int(stack[top].token[0])), "NUMBER"), []))
        elif symbol == "/":
            try:
                stack.append(ASTNode((str(int(stack[top - 1].token[0]) // int(stack[top].token[0])), "NUMBER"), []))
            except ZeroDivisionError:
                raise Exception("Division by zero")
        else:
            raise Exception(f"Unknown symbol '{symbol}'")
        stack.pop(top - 2)
        stack.pop(top - 2)
        stack.pop(top - 2)
    else:
        stack.append(linear.pop())

    return eval(linear, stack)
    
def stackToString(stack):
    string = ""
    for node in stack:
        string += str(node.token)
    return string

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

        output = evaluate(ast)
        output_lines.append(f"\nOutput: {output.token[0]}")

    except Exception as e:
        output_lines.append("Error: " + str(e))

    with open(output_file, 'w') as o:
        for line in output_lines:
            o.write(line + "\n")