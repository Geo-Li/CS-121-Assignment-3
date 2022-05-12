# This file is for Milestone 2 of Assignment 3
import ijson
from collections import defaultdict

# ░░░░░░▄▀▒▒▒▒░░░░▒▒▒▒▒▒▒▒▒▒▒▒▒█░░░░░░░░
# ░░░░░█▒▒▒▒░░░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█░░░░░░░
# ░░░░█▒▒▄▀▀▀▀▀▄▄▒▒▒▒▒▒▒▒▒▄▄▀▀▀▀▀▀▄░░░░░
# ░░▄▀▒▒▒▄█████▄▒█▒▒▒▒▒▒▒█▒▄█████▄▒█░░░░
# ░█▒▒▒▒▐██▄████▌▒█▒▒▒▒▒█▒▐██▄████▌▒█░░░
# ▀▒▒▒▒▒▒▀█████▀▒▒█▒░▄▒▄█▒▒▀█████▀▒▒▒█░░
# ▒▒▐▒▒▒░░░░▒▒▒▒▒█▒░▒▒▀▒▒█▒▒▒▒▒▒▒▒▒▒▒▒█░
# ▒▌▒▒▒░░░▒▒▒▒▒▄▀▒░▒▄█▄█▄▒▀▄▒▒▒▒▒▒▒▒▒▒▒▌
# ▒▌▒▒▒▒░▒▒▒▒▒▒▀▄▒▒█▌▌▌▌▌█▄▀▒▒▒▒▒▒▒▒▒▒▒▐
# ▒▐▒▒▒▒▒▒▒▒▒▒▒▒▒▌▒▒▀███▀▒▌▒▒▒▒▒▒▒▒▒▒▒▒▌
# ▀▀▄▒▒▒▒▒▒▒▒▒▒▒▌▒▒▒▒▒▒▒▒▒▐▒▒▒▒▒▒▒▒▒▒▒█░
# ▀▄▒▀▄▒▒▒▒▒▒▒▒▐▒▒▒▒▒▒▒▒▒▄▄▄▄▒▒▒▒▒▒▄▄▀░░
# ▒▒▀▄▒▀▄▀▀▀▄▀▀▀▀▄▄▄▄▄▄▄▀░░░░▀▀▀▀▀▀░░░░░
# ▒▒▒▒▀▄▐▒▒▒▒▒▒▒▒▒▒▒▒▒▐░░░░░░░░░░░░░░░░░

# 1. Open the json file
# For each token we're searching for, look up in json file
# Find intersecting docIDs --> docIDs that contain all query tokens

class Retrieve:
    def __init__(self, inverted_index_dict: dict):
        self._setup = True
        # key(string): token, value(dictionary): (filenameIDNum, frequency)
        self._inverted_index_dict = inverted_index_dict

        self._token_dict = defaultdict(dict)


    def updateInvertedIndexDict(self, new_inverted_index_dict):
        self._inverted_index_dict = new_inverted_index_dict


    """
    Pass in a token and return the docId from the frequency dictionary
    Args:
        token(str):
    Return:
        
    """
    def extractDocId(self, token: str) -> set:
        # result = set()
        # for json in /Report:
        #   if json is an invertedIndex:
        #       if token in json
        #           result.add(docIds associated with token)

        # When we want to find a docId that contains multiple tokens, then call this function on each token
        # Find and return intersection of sets

        docIds = set()

        if token in self._inverted_index_dict.keys():
            docIds.add(self._inverted_index_dict[token][0])

        # if we cannot find the token in the existing inverted index dictionary
        else:
            return set()



    """
    Update the token_dict with the updated inverted_index_dict

    Args:
        keywords(list): a list that contains the keyword from the query
    """
    def updateTokenDict(self, keywords):
        for token, frequency_dict in self._inverted_index_dict.items():
            if token in keywords:
                for docId, frequency in frequency_dict.items():
                    self._token_dict[token][docId] = frequency



    """
    AND the keywords and store them into a dictionary

    Args:
        keywords(list): a list that contains the keyword from the query

    Returns:
        Dictionary: a dictionary that has docId as the key, and the corresponding value frequency as the value
    """

    # ["stupid", "professor", "klefstad"]
    # [0, 1, 1]
    # [34597823045, 5, 5]


    def AND(self, keywords):
        dictSize = len(keywords)
        # key(string): docId, value(dictionary): (token, frequency)
        file_dict = defaultdict(dict)
        # key(string): docId, value(list): [token_frequency(int)]
        frequency_indicator_dict = defaultdict(lambda: [i-i for i in range(dictSize)])
        for keyword in keywords:
            # tokenOccurence = self.extractDocId(keyword)
            for key, val in self._token_dict.items():
                for docId, frequency in val.items():
                    file_dict[docId][key] = frequency
        for docId, token_dict in file_dict.items():
            for index in range(len(keywords)):
                # if the keyword is in the file, modify the list based on the frequency
                if keyword in token_dict.keys():
                    frequency_indicator_dict[docId][index] = token_dict[keyword]
                # if the keyword is not in the file, modify the list[index] into 0
                else:
                    frequency_indicator_dict[docId][index] = 0
        return frequency_indicator_dict


    # add up the frequency
    def pageRank(self, frequency_indicator_dict):
        page_rank_dict = dict()
        for docId, frequency_list in frequency_indicator_dict.items():
            # if all the keywords are presented in the page, then sum up the word frequencies
            if 0 not in frequency_list:
                page_rank_dict[docId] = sum(frequency_list)
        # sort the page based on their keywords frequencies in ascending order
        page_rank_dict = dict(sorted(page_rank_dict.items(), key = lambda item: item[1]))
        return page_rank_dict


    def convertDocId(self, page_rank_dict):
        pass



if __name__ == "__main__":
    ls = defaultdict(lambda: [i-i for i in range(5)])
    print(ls["true"])



