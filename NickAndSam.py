"""
COMP 141: Course Project
Phase 3.2: Evaluator for Lexp

This program integrates a scanner (Phase 1.2) and a parser for Lexp.
It reads an input file (with a single expression), tokenizes it, and then parses
the tokens to build an abstract syntax tree (AST). The tokens and AST are printed
to the output file.
"""

import sys
from parser_2_2 import *


def eval_expr(node: ASTNode, memory: dict):
    token, typ = node.token
    if typ == "NUMBER":
        return int(token)
    if typ == "IDENTIFIER":
        if token not in memory:
            raise Exception(f"Undefined identifier '{token}'")
        return int(memory[token])
    if token == '+':
        return int(eval_expr(node.children[0], memory) + eval_expr(node.children[1], memory))
    if token == '-':
        res = eval_expr(node.children[0], memory) - eval_expr(node.children[1], memory)
        return int(res if res >= 0 else 0)
    if token == '*':
        return int(eval_expr(node.children[0], memory) * eval_expr(node.children[1], memory))
    if token == '/':
        denom = eval_expr(node.children[1], memory)
        if denom == 0:
            raise Exception("Division by zero")
        return int(eval_expr(node.children[0], memory) // denom)
    raise Exception(f"Unknown expression node '{token}'")


def flatten_sequence(node):
    if node.token[0] == ';':
        left, right = node.children
        return flatten_sequence(left) + flatten_sequence(right)
    return [node]


def evaluate(ast):
    memory = {}
    stmts = flatten_sequence(ast)
    idx = 0
    while idx < len(stmts):
        stmt = stmts[idx]
        op, typ = stmt.token
        if op == ':=':
            ident_node, expr_node = stmt.children
            val = eval_expr(expr_node, memory)
            memory[ident_node.token[0]] = val
            stmts.pop(idx)
            continue
        if op == 'IF-STATEMENT':
            cond, then_stmt, else_stmt = stmt.children
            cond_val = eval_expr(cond, memory)
            branch = then_stmt if cond_val > 0 else else_stmt
            stmts.pop(idx)
            stmts[idx:idx] = flatten_sequence(branch)
            continue
        if op == 'WHILE-LOOP':
            cond, body = stmt.children
            cond_val = eval_expr(cond, memory)
            stmts.pop(idx)
            if cond_val > 0:
                stmts[idx:idx] = flatten_sequence(body) + [stmt]
            continue
        if op == 'skip':
            stmts.pop(idx)
            continue
        raise Exception(f"Unexpected statement node '{op}' in evaluation")
    return memory


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python evaluator_3_2.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    all_tokens = []
    output_lines = []

    try:
        with open(input_file, 'r') as infile:
            for line in infile:
                text = line.rstrip("\n")
                tokens = parseLine(text)
                if not tokens:
                    continue
                output_lines.append("Line: " + text)
                for val, typ in tokens:
                    output_lines.append(f"{val} : {typ}")
                output_lines.append("")
                all_tokens.extend(tokens)

        output_lines.insert(0, "Tokens:")

        ast = parse_tokens(all_tokens)
        output_lines.append("AST:")
        for line in collect_ast(ast):
            output_lines.append(line)

        memory = evaluate(ast)
        output_lines.append("")
        output_lines.append("Output:")
        for name, val in memory.items():
            output_lines.append(f"{name} = {val}")

    except Exception as e:
        output_lines.append("Error: " + str(e))

    with open(output_file, 'w') as outfile:
        for line in output_lines:
            outfile.write(line + "\n")