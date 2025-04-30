"""
COMP 141: Course Project
Phase 3.2: Evaluator for Lexp

This program integrates a scanner (Phase 1.2) and a parser (Phase 2.2) for Lexp.
It reads an input file, tokenizes it, and then parses the tokens to build an abstract syntax tree (AST).
The program then evaluates the AST and writes the results to an output file.
"""

import sys
from parser_2_2 import *


def eval_expr(node: ASTNode, memory: dict):
    """
    Recursively evaluate an expression AST and return its integer value.
    """
    token, typ = node.token
    if typ == "NUMBER":
        return int(token)
    if typ == "IDENTIFIER":
        if token not in memory:
            raise Exception(f"Undefined identifier '{token}'")
        return int(memory[token])
    # operator node: children [left, right]
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
    """
    Flatten a tree of sequencing (';') nodes into a Python list of statement ASTNodes.
    """
    if node.token[0] == ';':
        left, right = node.children
        return flatten_sequence(left) + flatten_sequence(right)
    return [node]


def evaluate(ast):
    """
    Iteratively evaluates the AST by performing base-statement rewritings on a statement list.
    Returns the final memory mapping identifiers to values.
    """
    memory = {}
    stmts = flatten_sequence(ast)
    idx = 0
    while idx < len(stmts):
        stmt = stmts[idx]
        op, typ = stmt.token
        # Assignment
        if op == ':=':
            ident_node, expr_node = stmt.children
            val = eval_expr(expr_node, memory)
            memory[ident_node.token[0]] = val
            # remove this statement
            stmts.pop(idx)
            continue
        # If-statement
        if op == 'IF-STATEMENT':
            cond, then_stmt, else_stmt = stmt.children
            cond_val = eval_expr(cond, memory)
            branch = then_stmt if cond_val > 0 else else_stmt
            # replace this stmt with branch flattened
            stmts.pop(idx)
            stmts[idx:idx] = flatten_sequence(branch)
            continue
        # While-loop
        if op == 'WHILE-LOOP':
            cond, body = stmt.children
            cond_val = eval_expr(cond, memory)
            # if true, execute body then re-add loop
            stmts.pop(idx)
            if cond_val > 0:
                stmts[idx:idx] = flatten_sequence(body) + [stmt]
            # else drop loop by not re-inserting
            continue
        # Skip
        if op == 'skip':
            stmts.pop(idx)
            continue
        # Unknown node
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
        # Scan tokens
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

        # Parse AST
        ast = parse_tokens(all_tokens)
        output_lines.append("AST:")
        for line in collect_ast(ast):
            output_lines.append(line)

        # Evaluate
        memory = evaluate(ast)
        output_lines.append("")
        output_lines.append("Output:")
        for name, val in memory.items():
            output_lines.append(f"{name} = {val}")

    except Exception as e:
        output_lines.append("Error: " + str(e))

    # Write to output
    with open(output_file, 'w') as outfile:
        for line in output_lines:
            outfile.write(line + "\n")