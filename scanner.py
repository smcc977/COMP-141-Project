import sys
import re

identifier = "^[a-zA-Z][a-zA-Z0-9]*$"
number = r"^[0-9]+$"
symbol = r"^[+\-*/()]+$"
#bool(re.fullmatch(pattern, text))

input_file = sys.argv[1]
output_file = sys.argv[2]

def checkRegex(text) -> tuple:
    return bool(re.fullmatch(identifier, text)), bool(re.fullmatch(number, text)), bool(re.fullmatch(symbol, text))


def parseLine(line):
    print(line)
    #make each element a tuple with token and type
    tokenList = []
    token = ()
    startIndex = 0
    count = 0
    validToken = False
    for char in line:
        #if char == upper or lower, keep going until non alphanumeric
        #if char == number and its the start of token, continue until non number
        #if char == symbol, it's its own token and next should be something else
        #if char == whitespace, end last token and start new
        #if char == non recognizable symbol, error
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
            #error
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