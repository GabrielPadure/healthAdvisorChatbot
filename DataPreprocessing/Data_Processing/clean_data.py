import json
import re


def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


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


def clean_data(data):
    """text cleaning to each entry in the dataset."""
    for item in data:
        item['clean_question'] = preprocess_text(item['question'])
        item['clean_answer'] = preprocess_text(item['answer'])
    return data


def save_data(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


input_file = '/DataPreprocessing/Resources/RawData/Symp&Cond.json'
output_file = '/DataPreprocessing/Resources/CleanData/clean_Symp&Cond.json'

data = load_data(input_file)
cleaned_data = clean_data(data)

save_data(cleaned_data, output_file)
