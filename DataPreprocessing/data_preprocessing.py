import re

import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer


def remove_punctuation(text):
    return re.sub(r'[^\w\s]', '', text)

def to_lowercase(text):
    return text.lower()

def tokenize_txt(texts):
    tokenized_texts = [word_tokenize(text) for text in texts]
    return tokenized_texts

def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    filtered_texts = [[token for token in tokens if token not in stop_words] for tokens in text]

    return filtered_texts

def apply_stemming(texts):
    stemmer = PorterStemmer()
    stemmed_texts = [[stemmer.stem(token) for token in tokens] for tokens in texts]
    return stemmed_texts

def apply_lemmatization(texts):
    lemmatizer = WordNetLemmatizer()
    lemmatized_texts = [[lemmatizer.lemmatize(token) for token in tokens] for tokens in texts]
    return lemmatized_texts

