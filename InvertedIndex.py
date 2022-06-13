import sys
import os
import json
from bs4 import BeautifulSoup
from collections import defaultdict
import math
from tokenizer import tokenize
from simhash import Simhash, SimhashIndex

MAX_INDEX_SIZE = 6000000 #About 6MB
DOCUMENT_COUNT = 42334      #Num of Files
LOW_TF_IDF = 1.8897566747311156 #What we consider low information TF-IDF SCORE
HTML_WEIGHTS = {
    "h1" : 7,
    "h2" : 6,
    "h3" : 5,
    "h4" : 4,
    "bold" : 3,
    "title" : 20
}

def mergeJSON(result, json1) -> dict:
    with open(json1) as file:
        partialIndex = json.load(file)
    result.update(partialIndex)
    return result


# """
# INDEX STRUCTURE DEPRECATED
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

# INDEX STRUCTURE
# {
#     String token: 
#     {
#         "totalFrequency": int frequency,
#         "docIds": {
#             {
#               Int docId : 
#                       String frequency: int frequencyScore, #Frequency score should
#                       String weight : int HTML_WEIGHT
#                       String "tfIDfScore" : 0
#             },
#             {
#               Int docId : 
#                       String frequency: int frequencyScore, #Frequency score should
#                       String weight : int HTML_WEIGHT
#                       String "tfIDfScore" : 0
#             }
#         }
#
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

"""
Calculation of TF * IDF SCORE and Build Index of Index
"""
def calculateIDFScoreAndIndexOfIndex(partialIndex):      
    indexOfIndex = dict()        
    with open("Report/invertedIndex/" + partialIndex, "r+") as outFile:
        data = json.load(outFile) 
    
    with open("Report/invertedIndex/" + partialIndex, "w+") as indexFile:
        indexFile.write("{\n")
        for num, token in enumerate(data.keys()):
            totalDocuments = len(data[token]["docIds"].keys())
            # print("totalDocument: ", totalDocuments)
            purgedDict = dict()
            for docId, posting in data[token]["docIds"].items():
                idf = math.log10( DOCUMENT_COUNT / totalDocuments)
                tf = 1 + math.log10(posting["frequency"])
                tfIdfScore = tf * idf
                # Filtering out documents with tfIdfScore < 1.8897566747311156 (LOW TF IDF SCORE)
                if tfIdfScore > LOW_TF_IDF:
                    posting["tfIDfScore"] = tfIdfScore
                else:
                    purgedDict[docId] = posting
            for k in purgedDict:
                if k in data[token]["docIds"].keys():
                    data[token]["docIds"].pop(k, None)
            if len(data.keys()) == (num+1):
                indexOfIndex[token] = indexFile.tell() #what byte are we on
                indexFile.write(f'"{token}": {json.dumps(data[token])}\n') #Don't add comma to the last one
                break
            indexOfIndex[token] = indexFile.tell() #what byte are we on
            indexFile.write(f'"{token}": {json.dumps(data[token])},\n') #one line couple
        indexFile.write("}")
    data.clear()
    print("Dumping indexOfIndex file: ", partialIndex)
    writeToIndex(partialIndex, indexOfIndex)
    print("Finish dumping indexOfIndex")

""""
Build the index of Index and revamps the invertedIndex to follow that
"""
def writeToIndex(partialIndex: str, indexOfIndex: dict):
    indexOfIndexName = "indexOf"+ str(partialIndex)
    with open("Report/invertedIndex/" + indexOfIndexName, "w+") as indexOfIndexFile:
        #call ijson on it -> find the seek() position -> seek into our Index.json
        json.dump(indexOfIndex, indexOfIndexFile)   
        

class InvertedIndex:
    def __init__(self):
        self._inverted_index_dict = dict()
        self._argv = None
        self._docID = defaultdict(str)
        self._numFile = 0
        self.simHash = SimhashIndex([], k = 0)
        self.pageNum = 1
        
        # 0-5, 6-b, c-h, i-n, o-t, u-z
        self.index_0_5 = open("Report/invertedIndex/index_0-5.json", "w+")
        self.index_6_b = open("Report/invertedIndex/index_6-b.json", "w+")
        self.index_c_h = open("Report/invertedIndex/index_c-h.json", "w+")
        self.index_i_n = open("Report/invertedIndex/index_i-n.json", "w+")
        self.index_o_t = open("Report/invertedIndex/index_o-t.json", "w+")
        self.index_u_z = open("Report/invertedIndex/index_u-z.json", "w+")
        
    
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

    def similarCheck(self, tokens : list) -> bool:
        """
        get_features from tokenize.py returns a list of all the tokens
        Simhash creates an entity of simhash and allows to compare with our simHashIndex
        """
        fingerPrint = Simhash(tokens)
        if self.simHash.get_near_dups(fingerPrint):
            return True
        else:
            self.simHash.add(str(self.pageNum), fingerPrint)
            return False
        
    
    def processJSONFile(self, file):
        with open(file) as JsonFile:
            # data here will be a dictionary that contains the url, content, and the encoding of the file
            data = json.load(JsonFile)
            
            #Add the numFile to the url
            html = data["content"]

            #Get the soup for Frequency and HTML tags
            soup = BeautifulSoup(html, 'html.parser')
            
            #Counts the file Frequency
            if (self.countFileFrequency(soup, self._numFile, data["url"])):
                #Calculate the Importance HTML tags
                self.tagWeight(soup, self._numFile)
            
            if sys.getsizeof(self._inverted_index_dict) >= MAX_INDEX_SIZE:
                self.processRecorder()


    def countFileFrequency(self, soup: str, docId : int, url: str):
        text = soup.get_text()
        tokens = tokenize(text)
        
        #Check with simhash if it needs to process the website
        if self.similarCheck(tokens):
            return False
        
        self._docID[self._numFile] = url
        self._numFile += 1
        for token in tokens:
            # If token is not in the index, add it
            if token not in self._inverted_index_dict.keys():
                self._inverted_index_dict[token] = {"totalFrequency" : 0, "docIds" : dict()}

            if docId not in self._inverted_index_dict[token]["docIds"]:
                self._inverted_index_dict[token]["docIds"][docId] = {"frequency": 0, "weight": 0, "tfIDfScore": 0}
            self._inverted_index_dict[token]["docIds"][docId]["frequency"] += 1
            self._inverted_index_dict[token]["totalFrequency"] += 1
        
        return True
        
    def tagWeight(self, soup, docID):
        # Instead of adding a set value, we can instead, multiply the existing freq by a multiplier (e.g. 0.4)

        h1 = " ".join(list(text.get_text() for text in soup.find_all('h1')))
        h2 = " ".join(list(text.get_text() for text in soup.find_all('h2')))
        h3 = " ".join(list(text.get_text() for text in soup.find_all('h3')))
        bold = " ".join(list(text.get_text() for text in soup.find_all('b')))

        h1 = set(tokenize(h1))
        h2 = set(tokenize(h2))
        h3 = set(tokenize(h3))
        bold = set(tokenize(bold))
        
        #Don't need if statements when get_text() should of grab all the h1,h2,h3,and b and created them
        for word in h1:
            if word in self._inverted_index_dict and docID in self._inverted_index_dict[word]["docIds"]:
                self._inverted_index_dict[word]["docIds"][docID]["weight"] += HTML_WEIGHTS.get('h1', 1)
        for word in h2:
            if word in self._inverted_index_dict and docID in self._inverted_index_dict[word]["docIds"]:
                self._inverted_index_dict[word]["docIds"][docID]["weight"] += HTML_WEIGHTS.get('h2', 1)
        for word in h3:
            if word in self._inverted_index_dict and docID in self._inverted_index_dict[word]["docIds"]:
                self._inverted_index_dict[word]["docIds"][docID]["weight"] += HTML_WEIGHTS.get('h3', 1)
        for word in bold:
            if word in self._inverted_index_dict and docID in self._inverted_index_dict[word]["docIds"]:
                self._inverted_index_dict[word]["docIds"][docID]["weight"] += HTML_WEIGHTS.get('h4', 1)

    def processRecorder(self):
        
        def updateInvertedIndex(partialDict, invertedIndex):
            if len(partialDict) < 1:
                return 
            try:
                index = json.load(invertedIndex)
                invertedIndex.seek(0)
                for token in partialDict.keys():
                    if token not in index:
                        index[token] = {"totalFrequency" : 0, "docIds" : dict()}
                
                    index[token]["totalFrequency"] += partialDict[token]["totalFrequency"]
                    index[token]["docIds"].update(partialDict[token]["docIds"])
                        
                json.dump(index, invertedIndex, indent=1)
            except ValueError as e:
                json.dump(partialDict, invertedIndex, indent=1)
            invertedIndex.seek(0)
        
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
        self._inverted_index_dict.clear()
                    
        updateInvertedIndex(index05, self.index_0_5)
        index05.clear()

        updateInvertedIndex(index6B, self.index_6_b)
        index6B.clear()
        
        updateInvertedIndex(indexCH, self.index_c_h)
        indexCH.clear()

        updateInvertedIndex(indexIN, self.index_i_n)
        indexIN.clear()

        updateInvertedIndex(indexOT, self.index_o_t)
        indexOT.clear()
        
        updateInvertedIndex(indexUZ, self.index_u_z)
        indexUZ.clear()

        with open("Report/docID/docID_" + str(self.pageNum) + ".json", "w") as outFile:
            json.dump(self._docID, outFile, indent=1)
    
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
        self.index_0_5.close()
        self.index_6_b.close()
        self.index_c_h.close()
        self.index_i_n.close()
        self.index_o_t.close()
        self.index_u_z.close()

if __name__ == "__main__":
    docId = 0 # increment whenever we add any url to urlMapper
    urlMapper = dict() # key: docId, value: url
    
    obj = InvertedIndex()
    # obj.createIndexFiles()
    obj.extract()
    obj.batchProcess()
    
    print("Starting merging...")
    docIds = dict()
    count = 0
    for file in os.listdir("Report/docID"):
        if file.startswith("docID_"):
            docIds = mergeJSON(docIds, "Report/docID/" + file)

    with open("Report/invertedIndex/MergedDocID.json", "w+") as outFile:
        json.dump(docIds, outFile, indent=1)
    print("Finished Merging...")
    
    #1. Iterate through all the partialIndex 05-uz
    #2. For each partialIndex, go from 0-5, 6-b, c-h, i-n, o-t, u-z, have another dictionary where it will save the indexOfIndex[token] = tell(), then redump that partialIndex[key]  
    print("Start calculation Tf-Idf score")
    for file in os.listdir("Report/invertedIndex"):
        if file.endswith(".json"):
            if file.startswith("index_"):
                calculateIDFScoreAndIndexOfIndex(file)
    print("End calculation of Tf-Idf Score")

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

    