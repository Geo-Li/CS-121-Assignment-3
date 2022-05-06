import sys
import json
import os
import Posting as posting
from xxlimited import Str
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.request import urlopen
# from tokenizer import tokenize
import nltk
nltk.download('punkt')

from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from nltk import word_tokenize,sent_tokenize


class InvertedIndex:
    def __init__(self):
        # key(string): token, value(dictionary): (filenameIDNum, frequency)
        self._inverted_index_dict = dict()
        self._argv = None
        #Key (#fileNameIdNum: value (Str: url)
        self._docID = defaultdict(str)
        self._numFile = 0

    
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
            
    def countFileFrequency(self, html, docID):
            # for the sake of simplicity, I will not take broken html into consideration,
            # but BeautifulSoup should be able to detect it.
            soup = BeautifulSoup(html, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.extract() 
            text = soup.get_text()
            
            # tokens = nltk.word_tokenize(text)
            # tokens = tk.tokenize(text)
            
            tokenizer = RegexpTokenizer(r'\w+')
            tokens = tokenizer.tokenize(text)
            
            stemmer = PorterStemmer()
            tokens = [stemmer.stem(token) for token in tokens]
            
            for token in tokens:
                if token not in self._inverted_index_dict.keys():
                    self._inverted_index_dict[token] = defaultdict(int)
                self._inverted_index_dict[token][docID] += 1
            
            if len(self._inverted_index_dict) >= 10:
                with open("invertedIndices.json", "w") as outFile:
                    # json.dump(self._inverted_index_dict, outFile)
                    json.dump(self._inverted_index_dict, outFile, indent = 2)
                
                with open("docID.json", "w") as outFile:
                    json.dump(self._docID, outFile, indent = 2)
            

    def processRecorder(self):
        print("This function stores the process we had for the overall project, \
            and use them accordingly when you are dealing with the other functions.")
        
        # with open("invertedIndexes.json", "w") as outFile:
        #     json.dump(str(self._inverted_index_dict, outFile), indent = 2)
        
        # with open("docID.json", "w") as outFile:
        #     json.dump(str(self._inverted_index_dict, outFile), indent = 2)
            

        ######################################## ########################################
        # h1 = set(tokenize(soup.find_all('h1')))
        # h2 = set(tokenize(soup.find_all('h2')))
        # h3 = set(tokenize(soup.find_all('h3')))
        # bold = set(tokenize(soup.find_all('b')))

        # for i in h1:
        #     if i.string in self._inverted_index_dict:
        #         self._inverted_index_dict[i.string][file] += 4
        #     else:
        #         self._inverted_index_dict[i.string][file] = 5
        # for i in h2:
        #     if i.string in self._inverted_index_dict:
        #         self._inverted_index_dict[i.string][file] += 3
        #     else:
        #         self._inverted_index_dict[i.string][file] = 4
        # for i in h3:
        #     if i.string in self._inverted_index_dict:
        #         self._inverted_index_dict[i.string][file] += 2
        #     else:
        #         self._inverted_index_dict[i.string][file] = 3
        # for i in bold:
        #     if i.string in self._inverted_index_dict:
        #         self._inverted_index_dict[i.string][file] += 1
        #     else:
        #         self._inverted_index_dict[i.string][file] = 2
        ######################################## ########################################




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