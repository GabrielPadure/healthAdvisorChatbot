import pandas as pd
import json

from DataPreprocessing.Data_Processing.data_preprocessing import preprocess_question


def excel_to_json(excel_path, json_path):
    data = pd.read_excel(excel_path, usecols=[0, 1], header=None)
    data.columns = ['question', 'answer']
    data['keywords'] = data['question'].apply(preprocess_question)
    records = data.to_dict(orient='records')

    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(records, file, ensure_ascii=True,
                  indent=4)  # Use ensure_ascii=False to handle Unicode characters properly


def main():
    excel_path = '/DataPreprocessing/Resources/RawData/Fitness.json'
    json_path = '/DataPreprocessing/Resources/CleanData/clean_Fitness.json'
    excel_to_json(excel_path, json_path)
    print("Conversion completed successfully!")


if __name__ == "__main__":
    main()
