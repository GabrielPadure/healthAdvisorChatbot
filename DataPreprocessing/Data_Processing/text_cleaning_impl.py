import re


# just basic data cleaning
def preprocess_text(text):
    if not isinstance(text, str) or text == '':
        return ''

    text = text.lower()
    text = re.sub(r"’", "'", text)  # Normalize apostrophes, there was a problem with this
    #  contractions expanding
    contractions = {
        "what's": "what is", "i'm": "i am", "he's": "he is", "she's": "she is",
        "it's": "it is", "that's": "that is", "there's": "there is", "who's": "who is",
        "can't": "cannot", "won't": "will not", "don't": "do not", "doesn't": "does not",
        "didn't": "did not", "isn't": "is not", "aren't": "are not", "wasn't": "was not",
        "weren't": "were not", "you're": "you are", "they're": "they are", "we're": "we are",
        "let's": "let us"
    }
    pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in contractions.keys()) + r')\b')
    text = pattern.sub(lambda x: contractions[x.group()], text)

    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text
