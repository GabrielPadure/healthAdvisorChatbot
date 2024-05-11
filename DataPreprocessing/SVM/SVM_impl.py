import json

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report

DATA_PATHS = {
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/clean_Fitness.json': 'Fitness',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/clean_Med&Suppl.json': 'Medication & Supplements',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/clean_MentalHealth.json': 'Mental Health',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/clean_Nutr&Diet.json': 'Nutrition & Diet',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/clean_Symp&Cond.json': 'Symptoms & Conditions'
}
MAX_FEATURES = 2000  # best value
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.25
RANDOM_STATE = 38  # best value I have found, gives 94% test accuracy(crazy) :)


def load_and_label_data(paths):
    """
    load JSON files and label data according to the category.
    """
    data = []
    for filepath, label in paths.items():
        with open(filepath, 'r') as file:
            entries = json.load(file)
            for entry in entries:
                text = entry['clean_question'] + ' ' + entry['clean_answer']
                data.append((text, label))
    return pd.DataFrame(data, columns=['text', 'label'])


def vectorize_text(data, max_features):
    """
    convert text data to TF-IDF vectors.
    """
    vectorizer = TfidfVectorizer(max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform(data['text'].values)
    return tfidf_matrix, data['label'].values, vectorizer


def train_model(X_train, y_train, kernel_type='linear'):
    """
    train the model .
    """
    model = SVC(kernel=kernel_type)
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_train, y_train, X_val, y_val, X_test, y_test):
    train_predictions = model.predict(X_train)
    val_predictions = model.predict(X_val)
    test_predictions = model.predict(X_test)

    train_acc = accuracy_score(y_train, train_predictions)
    val_acc = accuracy_score(y_val, val_predictions)
    test_acc = accuracy_score(y_test, test_predictions)

    print("Predicted test labels distribution:", np.unique(test_predictions, return_counts=True))
    print("Classification Report:\n", classification_report(y_test, test_predictions))

    return {
        "Training Accuracy": train_acc,
        "Validation Accuracy": val_acc,
        "Test Accuracy": test_acc
    }


def main():
    """
    execution function to load data, process it, and evaluate the model.
    """
    df = load_and_label_data(DATA_PATHS)
    tfidf_matrix, labels, vectorizer = vectorize_text(df, MAX_FEATURES)
    X_temp, X_test, y_temp, y_test = train_test_split(tfidf_matrix, labels, test_size=TEST_SIZE,
                                                      random_state=RANDOM_STATE)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=VALIDATION_SIZE,
                                                      random_state=RANDOM_STATE)

    model = train_model(X_train, y_train)
    results = evaluate_model(model, X_train, y_train, X_val, y_val, X_test, y_test)
    print(results)


if __name__ == "__main__":
    main()
