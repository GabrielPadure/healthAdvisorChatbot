import json
from DataPreprocessing.Data_Processing.text_cleaning_impl import preprocess_text


def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def clean_data(data):
    """Apply text cleaning directly to each question and answer in the dataset."""
    for item in data:
        item['question'] = preprocess_text(item['question'])
        ##item['answer'] = preprocess_text(item['answer'])
    return data


def save_data(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# Example usage
input_file = '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/Symp&Cond.json'
output_file = '/DataPreprocessing/Resources/CleanData/WIthLabels/clean_Symp&Cond.json'

data = load_data(input_file)
cleaned_data = clean_data(data)
save_data(cleaned_data, output_file)
