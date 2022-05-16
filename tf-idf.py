import math


class tfidf:
    def __init__(self, inverted_index_dict: dict):
        self._setup = True
        # key(str): token, value(dict): (docId, frequency)
        self._inverted_index_dict = inverted_index_dict
        self._lexi_count = 0
    
    
    def lexiCount(self):
        lexi_count = 0
        for val in self._inverted_index_dict.values():
            for freq in val.values():
                lexi_count += freq
        self._lexi_count = lexi_count
        return lexi_count
        
    
    def weight(self, token, docId):
        # w_(t,d) = (1+log(tf_(t,d))) x log(N/df_t)
        token_freq = self._inverted_index_dict[token][docId]
        tf_score = 1 + math.log10(token_freq)
        # in the lecture slides, professor indicates that df_t is for the number of document 
        # that contains the token, but here I will sum up the frequency of the token in these documents
        doc_freq = 0
        # doc_freq = len(self._inverted_index_dict[token])
        for freq in self._inverted_index_dict[token].values():
            doc_freq += freq
        df_score = math.log10(self._lexi_count / doc_freq)
        weight = tf_score * df_score
        return weight
        
        