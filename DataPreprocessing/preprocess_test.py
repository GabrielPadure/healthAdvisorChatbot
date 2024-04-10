import pandas as pd
from DataPreprocessing.data_preprocessing import preprocess_question

def load_and_preprocess_questions(path_to_csv):

    # Read the CSV file into a DataFrame
    df = pd.read_csv(path_to_csv, encoding='utf-8-sig')

    # Assuming questions are in the first column, extract them into a list
    questions = df.iloc[:, 0].astype(str).tolist()

    # Preprocess each question using the predefined function
    preprocessed_questions = [preprocess_question(question) for question in questions]

    return preprocessed_questions

def main():
    # Specify the path to your CSV file containing the questions
    path_to_csv = 'mental_health.csv'  # Update this to the actual path

    # Load and preprocess the questions
    preprocessed_questions = load_and_preprocess_questions(path_to_csv)

    # Print the preprocessed questions
    for question in preprocessed_questions:
        print(question)

if __name__ == '__main__':
    main()
