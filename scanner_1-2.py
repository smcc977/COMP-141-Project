r'''COMP 141: Course Project
Phase 1.1
Scanner for Lexp

Nicholas Henricksen and Samuel McCollough

Code Description:
This program will take an input file and output a text file containing the tokens identified.

The input and output files are specified in the command line.
Please see README.md for instructions on how to use the program.'''

import sys
import re

# Regular expressions for the token types.
# Note: the SYMBOL token first checks for the two‐character ":=" operator.
token_re = re.compile(r"""
    (?P<KEYWORD>\b(?:if|then|else|endif|while|do|endwhile|skip)\b) |
    (?P<IDENTIFIER>[a-zA-Z][a-zA-Z0-9]*) |
    (?P<NUMBER>\d+) |
    (?P<SYMBOL>:=|[+\-*/();])
    """, re.VERBOSE)

# Whitespace pattern (to skip spaces, tabs, etc.)
whitespace_re = re.compile(r"\s+")

def parseLine(line):
    tokenList = []
    pos = 0
    while pos < len(line):
        # Skip any whitespace
        m_ws = whitespace_re.match(line, pos)
        if m_ws:
            pos = m_ws.end()
            if pos >= len(line):
                break
        # Try to match one of our token patterns at the current position.
        m = token_re.match(line, pos)
        if m:
            tokenType = m.lastgroup         # Which named group matched
            tokenValue = m.group(tokenType)
            tokenList.append((tokenValue, tokenType.upper()))
            pos = m.end()
        else:
            # If no pattern matches, output an error token for the offending character
            tokenList.append((line[pos], "ERROR READING"))
            break  # Stop tokenizing the line after an error.
    return tokenList

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    with open(input_file, 'r') as i, open(output_file, 'w') as o:
        for line in i:
            line = line.rstrip("\n")
            o.write("Line: " + line + "\n")
            tokens = parseLine(line)
            for token in tokens:
                # Write token value, a colon, and the token type (in uppercase)
                o.write(f"{token[0]} : {token[1]}\n")
            o.write("\n")