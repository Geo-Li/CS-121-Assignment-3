import sys
import json
# import urllib3
from bs4 import BeautifulSoup



##############################
# Recording the progess here
# def read_website_to_text(url):
#     page = urllib3.urlopen(url)
#     soup = BeautifulSoup(page, 'html.parser')
#     for script in soup(["script", "style"]):
#         script.extract() 
#     text = soup.get_text()
#     lines = (line.strip() for line in text.splitlines())
#     chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
#     text = '\n'.join(chunk for chunk in chunks if chunk)
#     return str(text.encode('utf-8'))
##############################




if __name__ == "__main__":
    # pwd1 = /Users/geo/Desktop/CS\ 121/Assignment\ 3/DEV/mailman_ics_uci_edu/42db35c21e0cdfecd633d316c56cf72b38bddddb19566deda5297f3f0dfabac2.json
    # pwd2 = /Users/geo/Desktop/CS\ 121/Assignment\ 3/DEV/hack_ics_uci_edu/789bf380967bc750af924c2eb1f37866167f1cef2debae388f13ebc7513f33c3.json
    file = sys.argv[1]

    
    # print the content in the html file
    with open(file) as JsonFile:
        html_dict = json.load(JsonFile)
        html_content = html_dict["content"]
        soup = BeautifulSoup(html_content, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = [line.strip() for line in text.splitlines()]
        # for line in lines:
        #     print(line)
        # chunks = [phrase.strip() for line in lines for phrase in line.split()]
        # text = "\n".join(chunk for chunk in chunks if chunk)
        # print(text)

        # for now I will not check the special characters
        tokens = list()
        for line in lines:
            words = line.split()
            for word in words:
                if word != "" and words != "\n" and word != "\t":
                    tokens.append(word)
        for i, token in enumerate(tokens):
            print(i, token)



