r'''COMP 141: Course Project
Phase 1.1
Scanner for Lexp

Nicholas Henricksen and Samuel McCollough

Code Description:
This program will take an input file and output a text file containing the tokens identified.

The input and output files are specified in the command line.
Please see README.md for instructions on how to use the program.'''

r'''import sys
import re

identifier = r"^[a-zA-Z][a-zA-Z0-9]*$"
number = r"^[0-9]+$"
symbol = r"^([+\-*/();]|:=)$"
#symbol = r"^(?:\+\-|\*|\/|\(|\)|;|:)$"
keyword = r"^(if|then|else|endif|while|do|endwhile|skip)$"
#bool(re.fullmatch(pattern, text))
whitespace = r"\s+"

input_file = sys.argv[1]
output_file = sys.argv[2]

def checkRegex(text) -> tuple:
    return bool(re.fullmatch(identifier, text)), bool(re.fullmatch(number, text)), bool(re.fullmatch(symbol, text)), bool(re.fullmatch(keyword, text))

def checkWhitespace(text) -> bool:
    return bool(re.fullmatch(whitespace, text))

def parseLine(line):
    print(line)
    tokenList = []
    token = None    #changed from tuple to None
    startIndex = 0
    count = 0
    text = ""
    validToken = False
    while count < len(line):
        text = line[startIndex:count + 1]
        resultID, resultNum, resultSymbol, resultKeyword = checkRegex(text)

        validToken = resultID or resultNum or resultSymbol or resultKeyword
        if validToken:
            if resultKeyword:
                token = (text, "keyword")
            elif resultID:
                token = (text, "identifier")        #change back to all ifs if there is issue
            elif resultNum:
                token = (text, "number")
            elif resultSymbol:
                if line[count] == ":":
                    if line[count+1] == "=":
                        token = (line[startIndex:count + 1], "symbol")
                        count += 1
                        continue
                    else:
                        token = None
                else:
                    token = (text, "symbol")

        else:
            if token is not None:               #added none check for index error, review later
                token = (text[:-1], token[1])
                tokenList.append(token)
                token = None
                count -= 1
            startIndex = count
            text = line[startIndex:count + 1]
            resultID, resultNum, resultSymbol, resultKeyword = checkRegex(text)
            if not resultID and not resultNum and not resultSymbol and not resultKeyword:
                if checkWhitespace(text):
                    startIndex += 1
                    count += 1
                    continue
                if text == ":" or text == "=":
                    count += 1
                    continue
                tokenList.append((line[count], "Error reading"))
                return tokenList
        count += 1
    if token is not None:  # added none check for index error, review later
        token = (text, token[1])
        tokenList.append(token)
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
        i.close()'''

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
