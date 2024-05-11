import sys
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import re

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


def remove_punctuation(text):
    """Remove punctuation from text."""
    return re.sub(r'[^\w\s]', '', text)


def to_lowercase(text):
    """Convert all characters in text to lowercase."""
    return text.lower()


def tokenize_txt(text):
    """Tokenize the text into words."""
    return word_tokenize(text)


def remove_stopwords(words):
    """Remove stopwords from a list of words."""
    stop_words = set(stopwords.words('english'))
    return [word for word in words if word not in stop_words]


def apply_stemming(words):
    """Apply stemming to a list of words."""
    stemmer = PorterStemmer()
    return [stemmer.stem(word) for word in words]


def apply_lemmatization(words):
    """Apply lemmatization to a list of words."""
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(word) for word in words]


def preprocess_question(question):
    """Apply all preprocessing steps to a single question."""
    question_no_punct = remove_punctuation(question)
    question_lower = to_lowercase(question_no_punct)
    tokenized_question = tokenize_txt(question_lower)
    no_stopwords_question = remove_stopwords(tokenized_question)
    stemmed_question = apply_stemming(no_stopwords_question)
    lemmatized_question = apply_lemmatization(stemmed_question)
    return ' '.join(lemmatized_question)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_question = sys.argv[1]
        print(preprocess_question(input_question))
