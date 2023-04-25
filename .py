# Time Complexity Calculation
# Please refer to comments in each function for more explanation on time complexity calculation.
# tokenize has a time complexity of O(n), since it is a linear process on the input file.
# computeWordFrequencies has a time complexity of O(n log n), due to Python's Timsort algorithm.
# printFrequencies has a time complexity of O(n), since it is a linear process on the final list of tokens.
# However, printing will take a bit more real time.

# Worst-case time complexity of the entire PartA: O(n log n).


import sys
import re
import codecs


# Matches a line of text to a regex pattern, returning a list of tokens that match.
def regexMatch(line: str):
    regexPattern = r'[a-zA-Z0-9]+'
    tokenList = re.findall(regexPattern, line.lower())

    return tokenList


# Given a file path, reads the file line-by-line and returns a list of tokens.
def tokenize(TextFilePath: str) -> list:
    regexPattern = re.compile(r'[a-zA-Z0-9]+')
    tokenList = []

    # Attempts to open a file using utf-8 encoding.
    try:
        file = codecs.open(TextFilePath, 'r', encoding='utf-8')

        lineNumber = 0

        # Reads each line in the file, matches it, and then reports it.
        # Has a time complexity of O(n), since we process each line (and each
        # token in that line), exactly once. As n grows, time grows linearly.
        for line in file.readlines():
            lineNumber = lineNumber + 1
            lineTokens = re.findall(regexPattern, line.lower())

            for token in lineTokens:
                tokenList.append(token)

        file.close()

        return tokenList

    except FileNotFoundError:
        # If the file is not found, report so.
        print("File not found. Please enter a valid file path.")
        sys.exit()
    except UnicodeDecodeError:
        # If it fails to decode, report the file as not a text file.
        print("File type not recognized. Please enter a valid text file.")
        sys.exit()


# Calculates the frequencies of a given list and returns a dictionary with token frequencies.
def computeWordFrequencies(tokenList: list) -> dict:
    countedTokens = {}

    # Counts each token in the token list.
    # Time complexity of O(n), since it processes each term exactly once.
    # As the size of the list n grows, time to process grows linearly.
    for token in tokenList:
        if token not in countedTokens:
            countedTokens[token] = 1
        else:
            countedTokens[token] = countedTokens[token] + 1

    # Sorts the list.
    # Uses Timsort, which has a worst-case time complexity of O(n log n).
    # Timsort is a stable sorting algorithm, derived from merge sort and
    # insertion sort. An insertion sort is used first, dividing the input
    # into consecutive smaller blocks called runs. Then these runs are merged using a merge sort.
    # Since merge sort's worst time complexity is O(n log n), our result is a time complexity
    # of O(n log n).
    sortedList = dict(sorted(countedTokens.items(), key=lambda x: (-x[1], x[0])))

    return sortedList


# Prints the frequencies of a sorted, computed token dictionary to the screen.
# Each entry is printed once, with a complexity of O(n).
def printFrequencies(frequencies: dict):
    # Prints each item in the dictionary.
    # Has a time complexity of O(n), since we process each item exactly once.
    for entry in frequencies.items():
        print(entry[0] + " = " + str(entry[1]))


if __name__ == '__main__':
    printFrequencies(computeWordFrequencies(tokenize(sys.argv[1])))
