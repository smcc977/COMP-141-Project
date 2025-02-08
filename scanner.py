import sys
import re

identifier = "^[a-zA-Z][a-zA-Z0-9]*$"
number = "[0-9]+"
symbol = "[+ - * / ( )]"
#bool(re.fullmatch(pattern, text))

input_file = sys.argv[1]
output_file = sys.argv[2]

def parseLine(line):
    print(line)
    index = 0
    for char in line:
        if index == 0:
            None

if __name__ == "__main__":
    inputList = []
    for line in input_file:
        inputList.append(line)
    for list in inputList:
        parseLine(line)