from cmath import log
from functools import partial
import sys
import spacy
import os
import re
import ijson
import ujson as json

from bs4 import BeautifulSoup
from collections import defaultdict
from sortedcontainers import SortedDict
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from json.decoder import JSONDecodeError
import string
# from nltk import word_tokenize, sent_tokenize fds

MAX_INDEX_SIZE = 1000000 #About 5 MB
DOCUMENT_COUNT = 55392

HTML_WEIGHTS = {
    "h1" : 7,
    "h2" : 6,
    "h3" : 5,
    "h4" : 4,
    "bold" : 3,
    "title" : 20
}

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

def mergeJSON(result, json1) -> dict:
    with open(json1) as file:
        partialIndex = json.load(file)

    result.update(partialIndex)
    return result


# """
# INDEX STRUCTURE
# {
#     String token : 
#     {
#         int docId: 
#         {
#             String token_frequency: int frequencyScore, #Frequency score should
#             String weight : int HTML_WEIGHT
#             String "tfIDfScore" : 0
#         }
#     }
# }

# DOCID STRUCTURE
# {
#     int DocId : String url
# }

# SCORE STRUCTURE
# {
#       "Cristina Lopes" dociD: 
#       {
#         String tfIdfScore : int scores (0) -> Query (increment)
#       }
#       "Uci the car" "the relevance (Uci, Car)"
#         "Cristina"
#         {
#             docId(2) : {
#                 "tfIDfScore" : 0
#             }
#         }
#         "Lopes"
#         {
#             docId(2) : {
#                 "tfIDfScore" : 0
#             }
#         }
# }



class InvertedIndex:
    def __init__(self):
        self._inverted_index_dict = SortedDict()
        self._argv = None
        self._docID = defaultdict(str)
        self._numFile = 0
        self.pageNum = 1

        #Tokenizer/Stemmer
        # self.tokenizer = RegexpTokenizer(r"[a-zA-Z0-9]+")
        self.tokenizer = spacy.load("en_core_web_sm")
        self.tokenizer.max_length = 6000000            #Roughly 2gbs?
        self.stemmer = SnowballStemmer(language='english')

        # 0-5, 6-b, c-h, i-n, o-t, u-z
        self.index_0_5 = open("Report/invertedIndex/index_0-5.json", "a+")
        # json.dump(dict(), self.index_0_5)
        self.index_6_b = open("Report/invertedIndex/index_6-b.json", "a+")
        # json.dump(dict(), self.index_6_b)
        self.index_c_h = open("Report/invertedIndex/index_c-h.json", "a+")
        # json.dump(dict(), self.index_c_h)
        self.index_i_n = open("Report/invertedIndex/index_i-n.json", "a+")
        # json.dump(dict(), self.index_i_n)
        self.index_o_t = open("Report/invertedIndex/index_o-t.json", "a+")
        # json.dump(dict(), self.index_o_t)
        self.index_u_z = open("Report/invertedIndex/index_u-z.json", "a+")
        # json.dump(dict(), self.index_u_z)



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

    def processJSONFile(self, file):
        with open(file) as JsonFile:
            # data here will be a dictionary that contains the url, content, and the encoding of the file
            data = json.load(JsonFile)

            #Add the numFile to the url
            html = data["content"]
            # print(data["url"])
            self._docID[self._numFile] = data["url"]
            #Get the soup for Frequency and HTML tags
            soup = BeautifulSoup(html, 'html.parser')

            #Counts the file Frequency
            self.countFileFrequency(soup, self._numFile)

            #Calculate the Importance HTML tags
            self.tagWeight(soup, self._numFile)

            self._numFile += 1
            # print("The size of ivnerted_indexdict: " , sys.getsizeof(self._inverted_index_dict))
            if sys.getsizeof(self._inverted_index_dict) >= MAX_INDEX_SIZE:
                # print("Does it come here?")
                self.processRecorder()


    def tokenize(self, text):
        text = text.replace("-", " ").replace("_", " ")
        text = text.translate(str.maketrans('', '', string.punctuation))
        tokensList = list()
        expression = r"[a-zA-Z0-9]+"
        tokens = self.tokenizer(text)
        for word in re.finditer(expression, tokens.text):
            start, end = word.span()
            word = tokens.char_span(start, end)
            if not word:
                continue
            else:
                word = word.text
            word = self.stemmer.stem(word.strip())
            if len(word) < 2 or word in STOP_WORDS: #Maybe take this out later
                continue
            tokensList.append(word)
        return tokensList

    def countFileFrequency(self, soup, docID):
        # for the sake of simplicity, I will not take broken html into consideration,
        # but BeautifulSoup should be able to detect it.
        # for content in soup.find_all('body'):     #Not just the body(maybe?)

        text = soup.get_text()
        tokens = self.tokenize(text)

        for word in tokens:
            if word not in self._inverted_index_dict.keys():
                self._inverted_index_dict[word] = {}
                self._inverted_index_dict[word][docID] = {"frequency": 0, "weight": 0, "tfDfScore": 0}
            elif docID not in self._inverted_index_dict:
                self._inverted_index_dict[word][docID] = {"frequency": 0, "weight": 0, "tfDfScore": 0}
            self._inverted_index_dict[word][docID]["frequency"] += 1

            # tokens = [idx for idx in tokens if not re.findall("[^\u0000-\u05C0\u2100-\u214F]+", idx)]  #Handle bad input
            # print(tokens)

        # tokens = nltk.word_tokenize(text)
        # tokens = tk.tokenize(text)

    """
    Unsure if this works but trying to calculate tdIDFScore
    """
    def calculateIDFScore(self):

        with open("SeekJson/MergedIndex.json") as outFile:
            data = json.load(outFile)

        for token in data.keys():
            for docId in data[token]:
                print(docId)
                idf = log( DOCUMENT_COUNT / (1 + data[token]["frequency"]), 10)
                #Wrong frequency (Need to get all the tokens found in the occurrences)
                tf = data[token][docId]["frequency"]
                data[token][docId]["tfIdfScore"] = tf * idf

        with open("SeekJson/MergedIndex.json", "w") as outFile:
            data = json.dumps(outFile, indent=1)


    def tagWeight(self, soup, docID):
        # Instead of adding a set value, we can instead, multiply the existing freq by a multiplier (e.g. 0.4)

        h1 = " ".join(list(text.get_text() for text in soup.find_all('h1')))
        h2 = " ".join(list(text.get_text() for text in soup.find_all('h2')))
        h3 = " ".join(list(text.get_text() for text in soup.find_all('h3')))
        bold = " ".join(list(text.get_text() for text in soup.find_all('b')))

        h1 = set(self.tokenize(h1))
        h2 = set(self.tokenize(h2))
        h3 = set(self.tokenize(h3))
        bold = set(self.tokenize(bold))

        #Don't need if statements when get_text() should of grab all the h1,h2,h3,and b and created them
        for word in h1:
            word = self.stemmer.stem(word)
            if len(word) < 2 or word in STOP_WORDS: #Maybe take this out later
                continue
            if word in self._inverted_index_dict and docID in self._inverted_index_dict[word]:
                self._inverted_index_dict[word][docID]["weight"] += HTML_WEIGHTS.get('h1', 1)
        for word in h2:
            word = self.stemmer.stem(word)
            if len(word) < 2 or word in STOP_WORDS: #Maybe take this out later
                continue
            if word in self._inverted_index_dict and docID in self._inverted_index_dict[word]:
                self._inverted_index_dict[word][docID]["weight"] += HTML_WEIGHTS.get('h2', 1)
        for word in h3:
            word = self.stemmer.stem(word)
            if len(word) < 2 or word in STOP_WORDS: #Maybe take this out later
                continue
            if word in self._inverted_index_dict and docID in self._inverted_index_dict[word]:
                self._inverted_index_dict[word][docID]["weight"] += HTML_WEIGHTS.get('h3', 1)
        for word in bold:
            word = self.stemmer.stem(word)
            if len(word) < 2 or word in STOP_WORDS: #Maybe take this out later
                continue
            if word in self._inverted_index_dict and docID in self._inverted_index_dict[word]:
                self._inverted_index_dict[word][docID]["weight"] += HTML_WEIGHTS.get('h4', 1)


    #Learning how to sort (Key (alphabetically order) : DocID (increasing order) : value (unsorted))
    # ^ TA: Merge Sort, Binary Sort                   TreeMap
    #Splitting the newely sorted dictionary into smaller chunks (Easy part)
    #JSON1 A-G, JSON2 H-N, JSON3 O-S, JSON4 T-Z
    #apple: {1: 1}, apple : {2, 19}
    # Merge two JSON files, adding the values together if a shared key exists

    # No longer used  
    # def splitJSON(self) -> None:
    #     chunkSize = 1000
    #     for i in range(0, len(self._inverted_index_dict), chunkSize):
    #         with open("Report/invertedIndex_" + str(i//chunkSize) + '.json', 'w') as outfile:
    #             json.dump(self._inverted_index_dict[i:i+chunkSize], outfile)

    #1. Offload all the information into JSON objects 50000 keys, offload information to JSON
    #2. Call all the json objects and remerge them together

    def processRecorder(self):

        # alphaBetDict = {"0" : 0, "1" : 0, "2" : 0, "3" : 0, "4" : 0, "5" : 0, "6" : 0, "7" : 0, "8" : 0, "9" : 0, 
        #                 "a" : 0, "b" : 0, "c" : 0, "d" : 0, "e" : 0, "f" : 0, "g" : 0, "h" : 0, "i" : 0, "j" : 0, 
        #                 "k" : 0, "l" : 0, "m" : 0, "n" : 0, "o" : 0, "p" : 0, "q" : 0, "r" : 0, "s" : 0, "t" : 0, 
        #                 "u" : 0, "v" : 0, "w" : 0, "x" : 0, "y" : 0, "z" : 0}

        # json 0-5, 6-b, c-h, i-n, o-t, u-z
        # 1. Call a for loop for our partial inverted Index
        # 2. Map it to our alphaBetDict 
        # 3. Split it into chunks
        index05 = dict()
        index6B = dict()
        indexCH = dict()
        indexIN = dict()
        indexOT = dict()
        indexUZ = dict()

        for k,v in self._inverted_index_dict.items():
            firstChar = k[0]
            if firstChar in ['0', '1', '2', '3', '4', '5']:
                if k in index05:
                    index05[k].update(v)
                else:
                    index05[k] = v
            elif firstChar in ['6', '7', '8', '9', 'a', 'b']:
                if k in index6B:
                    index6B[k].update(v)
                else:
                    index6B[k] = v
            elif firstChar in ['c', 'd', 'e', 'f', 'g', 'h']:
                if k in indexCH:
                    indexCH[k].update(v)
                else:
                    indexCH[k] = v
            elif firstChar in ['i', 'j', 'k', 'l', 'm', 'n']:
                if k in indexIN:
                    indexIN[k].update(v)
                else:
                    indexIN[k] = v
            elif firstChar in ['o', 'p', 'q', 'r', 's', 't']:
                if k in indexOT:
                    indexOT[k].update(v)
                else:
                    indexOT[k] = v
            elif firstChar in ['u', 'v', 'w', 'x', 'y', 'z']:
                if k in indexUZ:
                    indexUZ[k].update(v)
                else:
                    indexUZ[k] = v

        try:
            index = json.load(self.index_0_5)
            self.index_0_5.seek(0)
            index.update(index05)
            json.dump(index, self.index_0_5, indent=1)
        except ValueError:
            if len(index05) > 0:
                json.dump(index05, self.index_0_5, indent=1)
        self.index_0_5.seek(0)
        index05.clear()

        try:
            index = json.load(self.index_6_b)
            self.index_6_b.seek(0)
            index.update(index6B)
            json.dump(index, self.index_6_b, indent=1)
        except ValueError:
            if len(index6B) > 0:
                json.dump(index6B, self.index_6_b, indent=1)
        self.index_6_b.seek(0)
        index6B.clear()

        try:
            index = json.load(self.index_c_h)
            self.index_c_h.seek(0)
            index.update(indexCH)
            json.dump(index, self.index_c_h, indent=1)
        except ValueError:
            if len(indexCH) > 0:
                json.dump(indexCH, self.index_c_h, indent=1)
        self.index_c_h.seek(0)
        indexCH.clear()

        try:
            index = json.load(self.index_i_n)
            index.update(indexIN)
            json.dump(index, self.index_i_n, indent=1)
        except ValueError:
            if len(indexIN) > 0:
                json.dump(indexIN, self.index_i_n, indent=1)
        self.index_i_n.seek(0)
        indexIN.clear()

        try:
            index = json.load(self.index_o_t)
            self.index_o_t.seek(0)
            index.update(indexOT)
            json.dump(index, self.index_o_t, indent=1)
        except ValueError:
            if len(index05) > 0:
                json.dump(indexOT, self.index_o_t, indent=1)
        self.index_o_t.seek(0)
        indexOT.clear()

        try:
            index = json.load(self.index_u_z)
            self.index_u_z.seek(0)
            index.update(indexUZ)
            json.dump(index, self.index_u_z, indent=1)
        except ValueError:
            if len(indexUZ) > 0:
                json.dump(indexUZ, self.index_u_z, indent=1)
        self.index_u_z.seek(0)
        indexUZ.clear()




        # with open("Report/invertedIndex_" + str(self.pageNum) + ".json", "w") as outFile:
        #     json.dump(self._inverted_index_dict, outFile, indent=1, sort_keys=True)

        with open("Report/docID/docID_" + str(self.pageNum) + ".json", "w") as outFile:
            json.dump(self._docID, outFile, indent=1)

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

        self.processRecorder()
        #1. Fix/Sort the mergeIndex (some values are null)
        #2. Implement word position in inverted index 
        #3. Index-Index Key(alpha(readline()[0])) -> Value (Position)  https://pypi.org/project/jsonslicer/

    # def createIndexFiles():
    #     print("Initalizing the indexes of the chunks in jsonFiles")
    #     # json 0-5, 6-b, c-h, i-n, o-t, u-z
    #     for num in range(1, 6):
    #         with open(f"invertedIndex/{num}.json", "w+") as file:
    #             json.dump(dict(), output)
    #     print("Finish initalizing the indexes of the hcunks of jsonFiles")


if __name__ == "__main__":
    docId = 0 # increment whenever we add any url to urlMapper
    urlMapper = dict() # key: docId, value: url

    obj = InvertedIndex()
    # obj.createIndexFiles()
    obj.extract()
    obj.batchProcess()

    result_index = obj._inverted_index_dict
    #MERGE docIDs and invertexIndices
    token_set = set(result_index.keys())
    num_docs = len(obj._docID)

    # for page in range(1, obj.pageNum):
    #     with open("Report/invertedIndex_" + str(page) + ".json", "r") as oldIndex:
    #         data = json.load(oldIndex)
    #         for tk in data.keys():
    #             token_set.add(tk)

    for page in range(1, obj.pageNum):
        with open("Report/docId/docID_" + str(page) + ".json", "r") as oldIndex:
            data = json.load(oldIndex)
            num_docs += len(data.keys())

    with open("Report/report.txt", "w") as outFile:
        outFile.write("Number of tokens: " + str(len(token_set)) + "\n")
        outFile.write("Number of documents: " + str(num_docs) + "\n")

    print("Starting merging...")
    # result = dict()
    docIds = dict()

    for file in os.listdir("Report"):
        if file.endswith(".json"):
            #         print("Report/" + file)
            #         if file.startswith("invertedIndex_"):
            #             result = mergeJSON(result, "Report/" + file)
            if file.startswith("docID_"):
                docIds = mergeJSON(docIds, "Report/" + file)

    # with open("SeekJson/MergedIndex.json", "w") as outFile:
    #     json.dump(result, outFile, indent=1)
    with open("SeekJson/MergedDocID.json", "w") as outFile:
        json.dump(docIds, outFile, indent=1)

    print("Finished Merging...")



    # print("Create indexOfIndex...")
    # IndexOfIndex = dict()
    # for num, key in enumerate(result.keys()):
    #     if key[0] not in IndexOfIndex: # key[0] gets the first character of the key
    #         IndexOfIndex[key[0]] = num 

    # with open("SeekJson/IndexOfIndex.json", "w") as outFile:
    #     json.dump(IndexOfIndex, outFile, indent=1)
    # print("Finish indexOfIndex...")

    # --- Everybody Shines Together ---
    # ⡗⢰⣶⣶⣦⣝⢝⢕⢕⠅⡆⢕⢕⢕⢕⢕⣴⠏⣠⡶⠛⡉⡉⡛⢶⣦⡀⠐⣕⢕
    # ⡝⡄⢻⢟⣿⣿⣷⣕⣕⣅⣿⣔⣕⣵⣵⣿⣿⢠⣿⢠⣮⡈⣌⠨⠅⠹⣷⡀⢱⢕
    # ⡝⡵⠟⠈⢀⣀⣀⡀⠉⢿⣿⣿⣿⣿⣿⣿⣿⣼⣿⢈⡋⠴⢿⡟⣡⡇⣿⡇⡀⢕
    # ⡝⠁⣠⣾⠟⡉⡉⡉⠻⣦⣻⣿⣿⣿⣿⣿⣿⣿⣿⣧⠸⣿⣦⣥⣿⡇⡿⣰⢗⢄
    # ⠁⢰⣿⡏⣴⣌⠈⣌⠡⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣬⣉⣉⣁⣄⢖⢕⢕⢕
    # ⡀⢻⣿⡇⢙⠁⠴⢿⡟⣡⡆⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣵⣵⣿
    # ⡻⣄⣻⣿⣌⠘⢿⣷⣥⣿⠇⣿⣿⣿⣿⣿⣿⠛⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    # ⣷⢄⠻⣿⣟⠿⠦⠍⠉⣡⣾⣿⣿⣿⣿⣿⣿⢸⣿⣦⠙⣿⣿⣿⣿⣿⣿⣿⣿⠟
    # ⡕⡑⣑⣈⣻⢗⢟⢞⢝⣻⣿⣿⣿⣿⣿⣿⣿⠸⣿⠿⠃⣿⣿⣿⣿⣿⣿⡿⠁⣠
    # ⡝⡵⡈⢟⢕⢕⢕⢕⣵⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣿⣿⣿⣿⣿⠿⠋⣀⣈⠙



    # with open("SeekJson/MergedIndex.json", "r") as oldIndex:
    # oldIndex.seek(2)
    # oldIndex.seek(2)
    # print(oldIndex.readline())
    # partialIndex = json.loads(oldIndex.) #Key, value iterator
    # print(type(partialIndex))
    # print(partialIndex)
    # kv = sorted([(k, v) for k, v in partialIndex], key=lambda x: x[1], reverse=True)
    # print(kv[:10])
    # print("The read line is: " + oldIndex.readline())
    # data = json.load(oldIndex)
    # print(data)

    # oldIndex.seek(1)
    #feb27_bias_in_machinelearn
    #jan16th_machinelearn
    #machinelearn

    # json 0-5, 6-b, c-h, i-n, o-t, u-z
    obj.index_0_5.close()
    obj.index_6_b.close()
    obj.index_c_h.close()
    obj.index_i_n.close()
    obj.index_o_t.close()
    obj.index_u_z.close()


    # token_pos.txt
    # 1. {"someToken": [(docId, freq), ...]}
    # 2. {"otherToken": [(docId, freq), ...]}
    # ...
    