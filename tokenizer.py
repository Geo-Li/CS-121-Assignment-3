from collections import defaultdict
from nltk.stem import PorterStemmer
import re
import sys
import string
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer

STOP_WORDS = set(['a', 'about', 'above', 'after', 'again', 'against', 'all', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are',
                 'aren\'t', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can\'t', 'cannot', 'could', 'couldn\'t', 'did',
                 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have',
                 'haven\'t', 'having', 'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i', 'i\'d', 'i\'ll',
                 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s', 'me', 'more', 'most', 'musntn\'t', 'my', 'myself', 'no', 'nor', 'not',
                 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 'she\'ll', 'she\'s', 
                 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 
                 'they\'d', 'they\'ll', 'they\'re', 'they\'ve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\d', 'we\'ll', 'we\'re', 'we\'ve',
                 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s','where', 'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would',
                 'wouldn\'t', 'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'])

# tokenizer = spacy.load("en_core_web_sm")
# tokenizer.max_length = 8000000            #Roughly 2gbs?
stemmer = SnowballStemmer(language='english')
tokenizer = RegexpTokenizer(r'[a-zA-Z0-9]{3,}')
"""
Time complexity is O(n), where n is the number of tokens in the text file.
"""
def tokenize(text):
        # text = text.replace("-", " ").replace("_", " ")
        # text = text.translate(str.maketrans('', '', string.punctuation))
        tokensList = list()
        expression = r"[a-zA-Z0-9]+"
        tokens = tokenizer.tokenize(text)
        for word in tokens:
            # start, end = word.span()
            # word = tokens.char_span(start, end)
            # if not word:
                # continue
            # else:
                # word = word.text
                # word = stemmer.stem(word)      #Stems the word during the tokenizer
            word = stemmer.stem(word)
            if word in STOP_WORDS: #Maybe take this out later
                continue
            tokensList.append(word)
        return tokensList



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
    # input = sys.argv[1]
    tokens = tokenize(input)
    print(len(tokens))
    # freq = computeWordFrequencies(tokens)