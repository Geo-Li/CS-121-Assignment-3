from collections import defaultdict
from nltk.stem import PorterStemmer
import re
import sys

"""
Time complexity is O(n), where n is the number of tokens in the text file.
"""
def tokenize(words: str) -> list:
    """
    Given a text file, returns a list of tokens.
    """
    result = []
    pattern = "[^A-Za-z0-9]+"
    ps = PorterStemmer()
    for word in words.split():
        word = re.sub(pattern, '', ps.stem(word))
        word = str([idx for idx in word if not re.findall("[^\u0000-\u05C0\u2100-\u214F]+", idx)])  #Handle bad input
        result.append(word.lower())
    print(words)
    return result


"""
Time complexity is O(n), where n is the number of tokens in the list of tokens.
"""
def computeWordFrequencies(tokens: list) -> dict:
    """
    Given a list of tokens, returns a dictionary of word frequencies.
    """
    freq = defaultdict(int)

    for word in tokens:
        freq[word] += 1

    return freq


if __name__ == "__main__":
    # input1 = "Documents/CS122B/assignment1/EvolutionofMarriageandFamily.txt"
    # input2 = "Documents/CS122B/assignment1/newAristocracy.txt"
    # input3 = "Documents/CS122B/assignment1/ProjectGutenbergeBook.txt"

    # print(tokenize(input1))
    # print(tokenize(input2))
    # print(tokenize(input3))

    # freq1 = computeWordFrequencies(tokenize(input1))
    # freq2 = computeWordFrequencies(tokenize(input2))
    # freq3 = computeWordFrequencies(tokenize(input3))

    # printFreq(freq1)
    # printFreq(freq2)
    # printFreq(freq3)

    # input = input("Enter the path of the text file: ")
    input = sys.argv[1]
    tokens = tokenize(input)
    freq = computeWordFrequencies(tokens)