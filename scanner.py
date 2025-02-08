import sys

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