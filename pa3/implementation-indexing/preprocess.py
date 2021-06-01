import string
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from bs4.element import Comment
from stopwords import stop_words_slovene


def process_text(html):
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.findAll(text=True)
    filtered_text = filter(keep_word, text)
    return get_words(filtered_text)


def process_word(word):
    word = word.strip(string.punctuation).lower()
    if word not in stop_words_slovene and word != '':
        return word
    return ''


def keep_word(word):
    remove_elements = ['style', 'script', 'noscript', 'head', 'title', 'meta', '[document]']

    if word.parent.name in remove_elements or isinstance(word, Comment) or word == '\n' or word.strip() == "":
        return False

    return True


def get_words(texts):
    words = []
    for text in texts:
        for word in word_tokenize(text):
            words.append(word)
    return words


def process_query(query):

    query = query.split()
    processed_query = []

    for word in get_words(query):
        word = process_word(word)
        if word != "":
            processed_query.append(word)

    return processed_query
