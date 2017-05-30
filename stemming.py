import nltk
from nltk.stem.snowball import PortugueseStemmer

portugueseStemmer = PortugueseStemmer()


def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed


def tokenize(text):
    tokens = nltk.word_tokenize(text, 'portuguese')
    stems = stem_tokens(tokens, portugueseStemmer)
    return stems
