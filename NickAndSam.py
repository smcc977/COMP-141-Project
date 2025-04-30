"""
COMP 141: Course Project
Phase 3.2: Evaluator for Lexp

This program integrates a scanner (Phase 1.2) and a parser for Lexp.
It reads an input file (with a single expression), tokenizes it, and then parses
the tokens to build an abstract syntax tree (AST). The tokens and AST are printed
to the output file.
"""

import sys
import re
from parser_2_2 import *

memory = {}

def isValidExpression(stack):
    return (len(stack) >= 3 and (stack[len(stack) - 1].token[1] == "NUMBER" or stack[len(stack) - 1].token[1] == "IDENTIFIER")
            and (stack[len(stack) - 2].token[1] == "NUMBER" or stack[len(stack) - 2].token[1] == "IDENTIFIER")
            and stack[len(stack) - 3].token[1] == "SYMBOL")

def isValidStatement(stack):
    return (len(stack) >= 3 and (stack[len(stack) - 1].token[1] == "NUMBER" or stack[len(stack) - 1].token[1] == "IDENTIFIER")
            and (stack[len(stack) - 2].token[1] == "NUMBER" or stack[len(stack) - 2].token[1] == "IDENTIFIER")
            and stack[len(stack) - 3].token[1] == "KEYWORD")


class LinearAST:
    def __init__(self, ast):
        self.nodes = self.push(ast)
        self.index = self.getIndex()

    def push(self, node, stack=[]):
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
        value0 = stack[top]
        value1 = stack[top - 1]
        if value0.token[1] == "IDENTIFIER":
            value0 = ASTNode(str(memory[value0.token[0]], "NUMBER"), [])
        if value1.token[1] == "IDENTIFIER":
            value1 = ASTNode(str(memory[value1.token[0]], "NUMBER"), [])
        if symbol == "+":
            stack.append(ASTNode((str(int(value1.token[0]) + int(value0.token[0])), "NUMBER"), []))
        elif symbol == "-":
            stack.append(ASTNode((str(int(value1.token[0]) - int(value0.token[0])), "NUMBER"), []))
            if int(stack[len(stack) - 1].token[0]) < 0:
                stack[len(stack) - 1].token = ("0", "NUMBER")
        elif symbol == "*":
            stack.append(ASTNode((str(int(value1.token[0]) * int(value0.token[0])), "NUMBER"), []))
        elif symbol == "/":
            try:
                stack.append(ASTNode((str(int(value1.token[0]) // int(value0.token[0])), "NUMBER"), []))
            except ZeroDivisionError:
                raise Exception("Division by zero")
        elif symbol == ":=":
            if value0.token[1] != "NUMBER":
                raise Exception("Assigning invalid type to an identifier.")
            memory.update({value1.token[0]: value0.token[0]})
            stack.append(ASTNode(str(value1.token[0], "SYMBOL"), []))
        else:
            raise Exception(f"Unknown symbol '{symbol}'")
        stack.pop(top - 2)
        stack.pop(top - 2)
        stack.pop(top - 2)
    elif isValidIf(stack):
        keyword = stack[top - 2].token[0]
        value0 = stack[top]
        value1 = stack[top - 1]
        if keyword == "if":
            #evaluate if function
        elif keyword == "else":
            stack.append(ASTNode((str(int(stack[top - 1].token[0]) - int(stack[top].token[0])), "NUMBER"), []))
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