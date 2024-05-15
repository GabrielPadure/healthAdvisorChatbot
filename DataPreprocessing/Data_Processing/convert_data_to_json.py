import pandas as pd
import json

# Assuming the preprocess_question function is correctly defined in the imported module
from DataPreprocessing.Data_Processing.data_preprocessing import preprocess_question


def excel_to_json(excel_path, json_path):
    # Read the Excel file, expecting headers at the first row and three specific columns
    data = pd.read_excel(excel_path, header=None, names=['label', 'question', 'answer'])

    # Convert the DataFrame to a list of dictionaries
    records = data.to_dict(orient='records')

    # Write the dictionary to a JSON file with proper formatting
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(records, file, ensure_ascii=False, indent=4)  # Set ensure_ascii to False for proper Unicode handling


def main():
    excel_path = '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/newdataset.xlsx'  # Correct the path and file extension
    json_path = '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/ComprehensiveMedicalQ&A.json'  # Correct the path for the JSON output
    excel_to_json(excel_path, json_path)
    print("Conversion completed successfully!")


if __name__ == "__main__":
    main()
