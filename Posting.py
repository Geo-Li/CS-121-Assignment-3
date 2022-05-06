import InvertedIndex

class Posting:
    def __init__(self, docid, tfidf, fields):
        self.docid = docid      #ID FILE
        self.tfidf = tfidf      #word Frequency
        self.fields = fields    #Does it come up in an important FIELD
        
    



if __name__ == "__main__":
    countFrequency = InvertedIndex()
    countFrequency.countFileFrequency("ANALYST/www_cs_edu/0a0056fb9a53ec6f190aa2b5fb1a97c33cd69726c8841f89d24fa5abd84d276c")
    
    
