import sys














input_file = sys.argv[1]
output_file = sys.argv[2]



def parseLine(line):
    print(line)
    #make each element a tuple with token and type
    tokenList = []
    indexStart = 0
    indexEnd = 0
    for char in line:
        #if char == upper or lower, keep going until non alphanumeric
        #if char == number and its the start of token, continue until non number
        #if char == symbol, it's its own token and next should be something else
        #if char == whitespace, end last token and start new
        #if char == non recognizable symbol, error
        currIndex = char.index()
        if char.isalpha:
            continue
        if char == " ":
            tokenList.append(line[0:char + 1])
            tokenList    
        

if __name__ == "__main__":
    inputList = []
    for line in input_file:
        inputList.append(line)
    for list in inputList:
        parseLine(line)