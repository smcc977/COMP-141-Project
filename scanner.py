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

tokenReg = re.compile(r"""
    (?P<KEYWORD>\b(?:if|then|else|endif|while|do|endwhile|skip)\b) |
    (?P<IDENTIFIER>[a-zA-Z][a-zA-Z0-9]*) |
    (?P<NUMBER>\d+) |
    (?P<SYMBOL>:=|[+\-*/();])
    """, re.VERBOSE)

whitespaceReg = re.compile(r"\s+")

def parseLine(line):
    tokenList = []
    pos = 0
    while pos < len(line):
        matchWhite = whitespaceReg.match(line, pos)
        if matchWhite:
            pos = matchWhite.end()
            if pos >= len(line):
                break
        tokenMatch = tokenReg.match(line, pos)
        if tokenMatch:
            tokenType = tokenMatch.lastgroup
            tokenValue = tokenMatch.group(tokenType)
            tokenList.append((tokenValue, tokenType))
            pos = tokenMatch.end()
        else:
            tokenList.append((line[pos], "ERROR READING"))
            break
    return tokenList

if __name__ == "__main__":
    inputFile = sys.argv[1]
    outputFile = sys.argv[2]
    with open(inputFile, 'r') as i:
        with open(outputFile, 'w') as o:
            for line in i:
                o.write(line.strip() + "\n")
                if (tokens := parseLine(line)) is not None:
                    for token in tokens:
                        o.write(token[1] + ": "+ token[0] + "\n")
                o.write("\n")
            o.close()
        i.close()
