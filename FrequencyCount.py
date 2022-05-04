import sys
import json
from collections import defaultdict



class FrequencyCount:
    def __init__(self):
        # key(string): token, value(dictionary): {filename, frequency}
        self._inverted_index_dict = defaultdict(dict)
    
    
    def extract(self):
        """
        Extract the file name from the command line

        Raises:
            Exception: if there is only one parameter which is the Python file name, then we have nothing
            to read as the input test file

        Returns:
            list: a list of arguments in type of string
        """
        if len(sys.argv) < 2:
            raise Exception("You need to specifiy the Python filename\
                and the input filename to let this program run")
        return sys.argv
        
    
    def countFileFrequency(self, file):
        with open(file) as JsonFile:
            # data here will be a dictionary that contains the url, content, and the encoding of the file
            data = json.load(JsonFile)
            
            # for the sake of simplisity, I will not take broken html into consideration,
            # but BeautifulSoup should be able to detect it.
        
        