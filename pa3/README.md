# IEPS project

In this project we have implemented the following:

A. data processing with indexing, \
B. data retrieval with inverted index (sqlite search) and \
C. data retrieval without inverted index (basic search)

**PREPARATION:**

1. Install and activate virtual environment (venv)

2. Import and download the nltk packages

>> import nltk \
>> nltk.download() 

3. Navigate to **implementation-indexing** folder: \
$ cd implementation-indexing

**RUN DATA PROCESSING AND INDEXING:**

To drop and fill the database tables again, run the following script:

$ python indexer.py

**RUN SQLITE SEARCH:**

Execute the following command with the desired query:

$ python run-sqlite-search.py param1 param2 ... paramX

**RUN BASIC SEARCH:**

Execute the following command with the desired query:

$ python run-basic-search.py param1 param2 ... paramX


