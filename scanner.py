'''
COMP 141: Course Project
Phase 1.1
Scanner for Lexp

Nicholas Henricksen and Samuel McCollough

Code Description:
This program will take an input file and output a text file containing the tokens identified.

The input and output files are specified in the command line.
Please see README.md for instructions on how to use the program.
'''

import sys
import re

identifier = r"^[a-zA-Z][a-zA-Z0-9]*$"
number = r"^[0-9]+$"
symbol = r"^[+\-*/()]+$"
#bool(re.fullmatch(pattern, text))

input_file = sys.argv[1]
output_file = sys.argv[2]

def checkRegex(text) -> tuple:
    return bool(re.fullmatch(identifier, text)), bool(re.fullmatch(number, text)), bool(re.fullmatch(symbol, text))


def parseLine(line):
    print(line)
    tokenList = []
    token = ()
    startIndex = 0
    count = 0
    validToken = False
    for char in line:
        text = line[startIndex:count + 1]
        resultID, resultNum, resultSymbol = checkRegex(text)

        validToken = resultID or resultNum or resultSymbol
        if validToken:
            if resultID:
                token = (text, "identifier")
            if resultNum:
                token = (text, "number")
            if resultSymbol:
                token = (text, "symbol")
        else:
            token = (text[:-1], token[1])
            tokenList.append(token)
            startIndex = count
            text = line[startIndex:count + 1]
            resultID, resultNum, resultSymbol = checkRegex(text)
            if not resultID and not resultNum and not resultSymbol:
                if char == " " or char == "\t" or char == "\n" or char == "\r":
                    startIndex += 1
                    count += 1
                    continue
                tokenList.append((line[count], "Error reading"))
                return tokenList
        count += 1
    return tokenList

if __name__ == "__main__":
    with open(input_file, 'r') as i:
        with open(output_file, 'w') as o:
            for line in i:
                o.write(line.strip() + "\n")
                if (tokens := parseLine(line)) is not None:
                    for token in tokens:
                        o.write(token[1] + ": "+ token[0] + "\n")
                o.write("\n")
            o.close()
        i.close()