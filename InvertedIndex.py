import sys
import json
import os
# import re

from bs4 import BeautifulSoup
from collections import defaultdict
from sortedcontainers import SortedDict
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
# from nltk import word_tokenize, sent_tokenize fds

MAX_INDEX_SIZE = 2500000 #About 2.5 MB

def mergeDict(dict1, dict2) -> dict:
    # result = {**dict1, **dict2} #MERGE SORT
    intersect = dict1 & dict2
    for key in intersect:
        dict1[key] = dict1[key] + dict2[key]

    return dict1


class InvertedIndex:
    def __init__(self):
        # key(string): token, value(dictionary): (filenameIDNum, frequency)
        self._inverted_index_dict = SortedDict()
        self._argv = None
        #Key (#fileNameIdNum: value (Str: url)
        self._docID = defaultdict(str)
        self._numFile = 0
        self.pageNum = 1


    def extract(self):
        """
        Extract the file name from the command line

        Raises:
            Exception: if there is only one parameter which is the Python file name, then we have nothing
            to read as the input test file

        # Returns:
        #     list: a list of arguments in type of string
        """

        # lets assume the path of the folder will be passed in to the second argv parameter
        if len(sys.argv) < 2:
            raise Exception("You need to specifiy the Python filename\
                and the input filename to let this program run")
        self._argv = sys.argv
        # return sys.argv

    # {
    #     "freq" : 12313123,
    #     "posting" : [             # posting is a list of postings (url mappings)
    #         {
    #             "docId" : 1,
    #             "url" : "http://www.google.com"
    #         }
    #     ]
    # }

    def processJSONFile(self, file):
        with open(file) as JsonFile:
            # data here will be a dictionary that contains the url, content, and the encoding of the file
            data = json.load(JsonFile)

            #Add the numFile to the url
            self._docID[self._numFile] = data["url"]

            #Counts the file Frequency
            html = data["content"]
            self.countFileFrequency(html, self._numFile)
            self._numFile += 1

            # print("The size of ivnerted_indexdict: " , sys.getsizeof(self._inverted_index_dict))
            if sys.getsizeof(self._inverted_index_dict) >= MAX_INDEX_SIZE:
                print("Does it come here?")
                self.processRecorder()


    def countFileFrequency(self, html, docID):
        # for the sake of simplicity, I will not take broken html into consideration,
        # but BeautifulSoup should be able to detect it.
        soup = BeautifulSoup(html, 'html.parser')
        tokenizer = RegexpTokenizer(r'\w+')
        stemmer = SnowballStemmer(language='english')
        # tokens = tokenizer.tokenize(text
        for content in soup.find_all('body'):
            for word in tokenizer.tokenize(content.get_text()):
                word = stemmer.stem(word)
                # tokens = [idx for idx in tokens if not re.findall("[^\u0000-\u05C0\u2100-\u214F]+", idx)]  #Handle bad input
                # print(tokens)
                if word not in self._inverted_index_dict.keys():
                    self._inverted_index_dict[word] = defaultdict(int)
                self._inverted_index_dict[word][docID] += 1

        # tokens = nltk.word_tokenize(text)
        # tokens = tk.tokenize(text)



        # print("Soup.find_all: ", soup.find_all('h1'))
        # h1 = set(tokenizer.tokenize(str(soup.find_all('h1'))))
        # h2 = set(tokenizer.tokenize(str(soup.find_all('h2'))))
        # h3 = set(tokenizer.tokenize(str(soup.find_all('h3'))))
        # bold = set(tokenizer.tokenize(str(soup.find_all('b'))))


        # Instead of adding a set value, we can instead, multiply the existing freq by a multiplier (e.g. 0.4)
        # for i in h1:
        #     if i in self._inverted_index_dict:
        #         self._inverted_index_dict[i][docID] += 4
        #     else:
        #         self._inverted_index_dict[i][docID] = 5
        # for i in h2:
        #     if i in self._inverted_index_dict:
        #         self._inverted_index_dict[i][docID] += 3
        #     else:
        #         self._inverted_index_dict[i][docID] = 4
        # for i in h3:
        #     if i in self._inverted_index_dict:
        #         self._inverted_index_dict[i][docID] += 2
        #     else:
        #         self._inverted_index_dict[i][docID] = 3
        # for i in bold:
        #     if i in self._inverted_index_dict:
        #         self._inverted_index_dict[i][docID] += 1
        #     else:
        #         self._inverted_index_dict[i][docID] = 2


    #Learning how to sort (Key (alphabetically order) : DocID (increasing order) : value (unsorted))
    # ^ TA: Merge Sort, Binary Sort                   TreeMap
    #Splitting the newely sorted dictionary into smaller chunks (Easy part)
    #JSON1 A-G, JSON2 H-N, JSON3 O-S, JSON4 T-Z
    #apple: {1: 1}, apple : {2, 19}
    # Merge two JSON files, adding the values together if a shared key exists

    # Replaced by code in if "__name__ " == "__main__":
    # def mergeAllJSONs(self):
    #     oldPageNum = self.pageNum - 1
    #     while oldPageNum >= 1:
    #         with open("Report/invertedIndex_" + str(oldPageNum) + ".json", "r") as oldIndex:
    #             data = json.load(oldIndex)
    #             new_data = mergeDict(data, self._inverted_index_dict)

    # We made this ourselves
    # It splits JSON files :)
    def splitJSON(self) -> None:
        chunkSize = 1000
        for i in range(0, len(self._inverted_index_dict), chunkSize):
            with open("Report/invertedIndex_" + str(i//chunkSize) + '.json', 'w') as outfile:
                json.dump(self._inverted_index_dict[i:i+chunkSize], outfile)

    #1. Offload all the information into JSON objects 50000 keys, offload information to JSON
    #2. Call all the json objects and remerge them together

    def processRecorder(self):
        # print("This function stores the process we had for the overall project, \
        #     and use them accordingly when you are dealing with the other functions.")
        # if self.pageNum >= 2:  # this is always going to be true???

        #Merge with the existing inverted index dict with old inverted index dict (data)

        # print(new_data)

        with open("Report/invertedIndex_" + str(self.pageNum) + ".json", "w") as outFile:
            json.dump(self._inverted_index_dict, outFile, indent = 2)

        with open("Report/docID_" + str(self.pageNum) + ".json", "w") as outFile:
            json.dump(self._docID, outFile, indent = 2)

        self._inverted_index_dict.clear()
        self._docID.clear()
        self.pageNum += 1


    def batchProcess(self):
        """
        Process the JSON file from DEV folder
        """
        # for now this funciton is only designed for DEV folder our professor provided to us
        path = self._argv[1]
        dir_list = os.listdir(path)

        for JsonFolder in dir_list:
            sub_path = os.path.join(path, JsonFolder)
            sub_dir_list = os.listdir(sub_path)
            for file in sub_dir_list:
                file_path = os.path.join(sub_path, file)
                self.processJSONFile(file_path)






# Call the class
if __name__ == "__main__":
    # docId = 0 # increment whenever we add any url to urlMapper
    # urlMapper = dict() # key: docId, value: url

    obj = InvertedIndex()
    obj.extract()
    obj.batchProcess()

    result_index = obj._inverted_index_dict
    #MERGE docIDs and invertexIndices
    token_set = set(result_index.keys())
    num_docs = len(obj._docID)

    for page in range(1, obj.pageNum):
        with open("Report/invertedIndex_" + str(page) + ".json", "r") as oldIndex:
            data = json.load(oldIndex)
            for tk in data.keys():
                token_set.add(tk)

        with open("Report/docID_" + str(page) + ".json", "r") as oldIndex:
            data = json.load(oldIndex)
            num_docs += len(data.keys())

    with open("Report/report.txt", "w") as outFile:
        outFile.write("Number of tokens: " + str(len(token_set)) + "\n")
        outFile.write("Number of documents: " + str(num_docs) + "\n")