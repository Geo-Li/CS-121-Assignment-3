--------------- CS 121 Assignment 3 ---------------
Team Members of: Geo Li(82784712), Ryan Luong(27248658), Bryan Phung(12937958)

1. Call the following line to execute all the pip installs required to run our program
>>> pip install -r requirements.txt
If requirements.txt does not work, you can manually install the libraries with these commands:
python3 -m pip install ujson
python3 -m pip install flask
python3 -m pip install beautifulsoup4
python3 -m pip install nltk

2. BEFORE you run inverted index python file, make ONE folder called "Report" which will contain TWO folders called "docID" and "InvertedIndex" (Should be within the folder however if ran from this file)
No quotations (""), just call them by the named specified up above. 

3. Also!!! Download and unzip the DEV folder professor provided before run the InvertedIndex.py file

4. To build the inverted index, run InvertedIndex.py with the DEV folder:
>>> python3 InvertedIndex.py DEV

5. To start your query processing, run app.py located in the root folder
>>> python3 app.py

6. A new window should open up in your default browser with a familiar-looking interface. It should have the domain of http://127.0.0.1:5000

7. To perform a query, enter your query in the search bar and hit the "Search" button... OR, if you're feeling risky, hit the "I'm Feeling Risky" button for a surprise