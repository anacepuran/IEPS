import os
import sqlite3
from preprocess import process_text, process_word


def indexer():

    directory = '../input'

    print('Indexing...')
    for file in os.listdir(directory):
        if file.endswith("html"):
            with open(os.path.join(directory, file), "r", encoding='utf8', errors='ignore') as f:
                html = f.read()
                words = process_text(html)
                unique_words = []
                for word in words:
                    word = process_word(word)
                    if word != "":
                        try:
                            write_to_index_word(word)
                        except Exception as e:
                            pass
                        if word not in unique_words:
                            generate_posting(word, words, file)
                            unique_words.append(word)


def generate_posting(word, words, file):
    index = []
    count_frequency = 0
    for i, element in enumerate(words):
        element = process_word(element)
        if element == word:
            index.append(i)
            count_frequency += 1
    try:
        write_to_posting(word, file, count_frequency, str(index)[1:len(str(index))-1])
    except Exception as e:
        pass


def write_to_index_word(word):
    conn = sqlite3.connect('inverted-index.db')
    c = conn.cursor()
    sql = "INSERT INTO IndexWord VALUES (?)"
    c.execute(sql, (word,))
    conn.commit()
    conn.close()


def write_to_posting(word, document, frequency, index):
    conn = sqlite3.connect('inverted-index.db')
    c = conn.cursor()
    sql = "INSERT INTO Posting VALUES  (?,?,?,?)"
    c.execute(sql, (word, document, frequency, index,))
    conn.commit()
    conn.close()


def create_database():

    conn = sqlite3.connect('inverted-index.db')
    c = conn.cursor()

    """c.execute('''
            DROP TABLE IndexWord;
        ''')
    c.execute('''
            DROP TABLE Posting;
        ''')"""
    c.execute('''
        CREATE TABLE IndexWord (
            word TEXT PRIMARY KEY
        );
    ''')

    c.execute('''
        CREATE TABLE Posting (
            word TEXT NOT NULL,
            documentName TEXT NOT NULL,
            frequency INTEGER NOT NULL,
            indexes TEXT NOT NULL,
            PRIMARY KEY(word, documentName),
            FOREIGN KEY (word) REFERENCES IndexWord(word)
        );
    ''')

    conn.commit()
    conn.close()


# to recreate database uncomment lines 66-71 (DROP TABLE)
create_database()
indexer()
