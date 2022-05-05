import urllib2
from bs4 import BeautifulSoup
url = 'http://www.google.co.in/'

conn = urllib2.urlopen(url)
html = conn.read()

soup = BeautifulSoup(html)
links = soup.find_all('a')

for tag in links:
    link = tag.get('href',None)
    if link is not None:
        print link








from collections import defaultdict

class PageRank:

    def __init__(self) -> None:
        self._PRdict = defaultdict(int)
        
    def evaluateContent(self, htmlContent):
        """
        Extract the url link from the html content page and store them into the page rank dictionary

        Args:
            htmlContent: the content of html, not the pure text content
            
        Returns:
            None
        """
        self._PRdict[page] += 1
        return

