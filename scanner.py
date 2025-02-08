import sys
import re

identifier = "^[a-zA-Z][a-zA-Z0-9]*$"
number = "[0-9]+"
symbol = "[+ - * / ( )]"
#bool(re.fullmatch(pattern, text))

input_file = sys.argv[1]
output_file = sys.argv[2]

def checkRegex(text) -> tuple:
    out = (False, False, False)
    out.first = bool(re.fullmatch(identifier, text))
    out.second = bool(re.fullmatch(number, text))
    out.third = bool(re.fullmatch(symbol, text))
    return out


def parseLine(line):
    print(line)
    #make each element a tuple with token and type
    tokenList = []
    token = ()
    indexStart = 0
    count = 0
    validToken = False
    for char in line:
        #if char == upper or lower, keep going until non alphanumeric
        #if char == number and its the start of token, continue until non number
        #if char == symbol, it's its own token and next should be something else
        #if char == whitespace, end last token and start new
        #if char == non recognizable symbol, error
        text = line[startIndex:count + 1]
        resultID = bool(re.fullmatch(identifier, text))
        resultNum = bool(re.fullmatch(number, text))
        resultSymbol = bool(re.fullmatch(symbol, text))

        validToken = resultID or resultNum or resultSymbol
        if resultID:
            token = (text, "identifier")
        if resultNum:
            token = (text, "number")
        if resultSymbol:
            token = (text, "symbol")
        if validToken == False:
            #error
            token.first = text[:-1]
            tokenList.append(token)
            startIndex = count
            resultID = bool(re.fullmatch(identifier, text))
            resultNum = bool(re.fullmatch(number, text))
            resultSymbol = bool(re.fullmatch(symbol, text))
            
            if not resultID and not resultNum and not resultSymbol:
                tokenList.append((line[count], "Error reading"))
                startIndex += 1

        count += 1

        
        
        currIndex = char.index()
        if char.isalpha:
            continue
        if char == " ":
            tokenList.append(line[0:char + 1])
            tokenList    
        

if __name__ == "__main__":
    with open(input_file, 'r') as i:
        with open(output_file, 'w') as o:
            for line in i:
                o.write(line)
                for token in parseLine(line):
                    o.write(token)
            o.close()
        i.close()