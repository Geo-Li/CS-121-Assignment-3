import ujson as json
from tokenizer import tokenize
from time import time
from collections import defaultdict
import heapq
from tkinter import *

invertedIndexNum = {
    2 : "Report/invertedIndex/index_6-b.json",
    1 : "Report/invertedIndex/index_0-5.json",
    3 : "Report/invertedIndex/index_c-h.json",
    4 : "Report/invertedIndex/index_i-n.json",
    5 : "Report/invertedIndex/index_o-t.json",
    6 : "Report/invertedIndex/index_u-z.json",
    7 : "Report/invertedIndex/MergedDocID.json"
}

#Returns a list of urls?
def handleQuery(query : str) -> list:
    #1. tokenize the term for the invertedIndex
    startTime = time()
    termsQuery = tokenize(query)
    partialIndex = dict()
    docIds = defaultdict(int)  #{docId : CombinedTfIDfScore}
    result = list()
    heapq.heapify(result)
    # maxHeap : (2, 3, 4, 5, 1) => (5, 2, 3, 4, 1) --- Used to easily get top n results
    
    #Should return an empty list
    if len(termsQuery) == 0:
        return []
    
    #1. Get set of query terms
    #2. For each term, find the invertedIndex containing the term
    #3. Retrieve term from invertedIndex and find the docIds
    #4. Build a set of docIds that contain all the terms
    #5. Calculate total TF-IDF score for each docId
    #6. Rank the docIds through TF-IDF score and return the top 10
    
    #1. Get set of query terms
    queryTerms = set(termsQuery)
    
    #2. For each term, find its posting from the invertedIndex
    #3. Retrieve term from invertedIndex and find the docIds
    #4. Build a set of docIds that contain all the terms
    print(queryTerms)
    for term in queryTerms:
        partialIndex.update(getTermDict(term))

    # Maps a token to a set of docIds
    termToDocIds = dict()
    for token in partialIndex.keys():
        termToDocIds[token] = extractDocId(token, partialIndex)
    
    # Get intersecting docIds from all terms in termToDocIds
    # greater than 8 tokens, union(intersection((4 token)), intersection((4 token), ..., intersection((n % 4 token))))
    relevantDocIds = getRelevantDocIds(termToDocIds)
    
    #5. Calculate total TF-IDF score for each docId 
    if len(relevantDocIds) == 0:
        print("Processing time: ", time() - startTime)
        return []

    for token in partialIndex.keys():
        for docId in relevantDocIds:
            if docId in partialIndex[token]["docIds"]:
                if partialIndex[token]["docIds"][docId]["weight"] == 0:
                    docIds[docId] += partialIndex[token]["docIds"][docId]["tfIDfScore"]
                else:
                    docIds[docId] += partialIndex[token]["docIds"][docId]["tfIDfScore"] * partialIndex[token]["docIds"][docId]["weight"]

    # Add the docIds to the heap
    for docId, score in docIds.items():
        heapq.heappush(result, (docId, score))
    
    #6. Rank the docIds through TF-IDF score and return the top 10
    retVal = getURLs(map(lambda x: x[0], heapq.nlargest(10, result, key=lambda x: x[1])))
    print("Processing time: ", time() - startTime)
    return retVal

def getRelevantDocIds(termToDocIds: dict) -> set:
    """
    Returns a set of docIds relevant to the query.
    If the query contains more than 8 tokens, split the query into groups of 4 tokens and find its intersection.
    At the end, union the results of the intersection of the 4 token queries.
    """
    relevantDocIds = set()
    if len(termToDocIds) <= 8:
        # If the query contains less than 8 tokens, return the union of the docIds
        relevantDocIds = set.union(*termToDocIds.values())
    else:
        # Split the query into groups of 4 tokens
        groups = [termToDocIds.keys()[i:(i + 4) if i + 4 < len(termToDocIds) else len(termToDocIds)] for i in range(0, len(termToDocIds), 4)]
        # Find the intersection of the 4 token queries
        for group in groups:
            relevantDocIds = set.intersection(*[termToDocIds[token] for token in group])
        
    return relevantDocIds



def getURLs(docIds: list) -> list:
    """
    Returns a list of docIDs associated with the given docIDs
    """
    urls = []

    with open(invertedIndexNum[7], "r") as file:
        data = json.load(file)
        for docId in docIds:
            urls.append(data[str(docId)])
    return urls
    
def getTermDict(queryTerm: str) -> dict:
    """
    Takes in a single query term and returns a dictionary of the term's posting from the inverted index
    """
    termDict = dict()
    def seekToFindInfo(invertedIndex, indexOfIndex):
        termDictInside = {}
        position = None
        with open(indexOfIndex, 'r') as index:
            position = json.load(index)
            position = position[queryTerm]
        if position:
            with open(invertedIndex, 'r') as index:
                index.seek(position)
                line = index.readline()
                if line.endswith(",\n"):
                    line = line[:-2]
                else:
                    line = line[:-1]
                termDictInside =  json.loads("{" + line + "}")
        return termDictInside
    
    firstChar = ord(queryTerm[0])
    # print("The queryTerm: " + queryTerm)
    if firstChar >= ord('0') and firstChar <= ord('5'):
        termDict = seekToFindInfo(invertedIndexNum[1], "Report/invertedIndex/indexOfindex_0-5.json")
    elif firstChar >= ord('6') and firstChar <= ord('b'):
        termDict = seekToFindInfo(invertedIndexNum[2], "Report/invertedIndex/indexOfindex_6-b.json")
    elif firstChar >= ord('c') and firstChar <= ord('h'):
        termDict = seekToFindInfo(invertedIndexNum[3], "Report/invertedIndex/indexOfindex_c-h.json")
    elif firstChar >= ord('i') and firstChar <= ord('n'):
        termDict = seekToFindInfo(invertedIndexNum[4], "Report/invertedIndex/indexOfindex_i-n.json")
    elif firstChar >= ord('o') and firstChar <= ord('t'):
        termDict = seekToFindInfo(invertedIndexNum[5], "Report/invertedIndex/indexOfindex_o-t.json")
    elif firstChar >= ord('u') and firstChar <= ord('z'):
        termDict = seekToFindInfo(invertedIndexNum[6], "Report/invertedIndex/indexOfindex_u-z.json")
                
    #Should return
    #{
    #   token: { 
    #           docID: {
    #            "frequency": 1,
    #            "weight": 0,
    #            "tfDfScore": 0
    #   } 
    #} 
    # print(termDict)
    return termDict
    
    
    
    
def extractDocId(token: str, partialIndex: dict) -> set:
    docIds = set()
    # print(partialIndex[token])

    if token in partialIndex:
        for docId in partialIndex[token]["docIds"].keys():
            docIds.add(docId)
    
    return docIds


if __name__ == "__main__":
    # print(handleQuery("how to learn computer science at uci irvine at machine learning ics hentai"))
    while True:
        query = input("Search: ")
        if query == "/End":
            break
        for num, i in enumerate(handleQuery(query), 1):
            print(f"{num}: {i}")
    
