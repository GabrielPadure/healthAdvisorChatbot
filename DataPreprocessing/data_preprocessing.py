import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Ensure you've downloaded the necessary NLTK data

def remove_punctuation(text):
    """Remove punctuation from a single text string."""
    return re.sub(r'[^\w\s]', '', text)

def to_lowercase(text):
    """Convert all characters in a single text string to lowercase."""
    return text.lower()

def tokenize_txt(text):
    """Tokenize a single text string into a list of words."""
    return word_tokenize(text)

def remove_stopwords(tokens):
    """Remove stopwords from a list of tokens."""
    stop_words = set(stopwords.words('english'))
    return [token for token in tokens if token not in stop_words]

def apply_stemming(tokens):
    """Apply stemming to a list of tokens."""
    stemmer = PorterStemmer()
    return [stemmer.stem(token) for token in tokens]

def apply_lemmatization(tokens):
    """Apply lemmatization to a list of tokens."""
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]

def preprocess_question(question):
    """Apply all preprocessing steps to a single question."""
    question_no_punct = remove_punctuation(question)
    question_lower = to_lowercase(question_no_punct)
    tokenized_question = tokenize_txt(question_lower)
    no_stopwords_question = remove_stopwords(tokenized_question)
    stemmed_question = apply_stemming(no_stopwords_question)
    lemmatized_question = apply_lemmatization(stemmed_question)
    return ' '.join(lemmatized_question)
