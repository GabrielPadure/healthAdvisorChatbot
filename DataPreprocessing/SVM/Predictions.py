from joblib import dump
from sklearn.model_selection import train_test_split

from DataPreprocessing.SVM.SVM_impl import load_and_label_data, DATA_PATHS, vectorize_text, MAX_FEATURES, \
    TEST_SIZE, RANDOM_STATE, VALIDATION_SIZE, train_model, evaluate_model


def main():
    df = load_and_label_data(DATA_PATHS)
    print("Data loaded and labeled.")  #checking
    tfidf_matrix, labels, vectorizer = vectorize_text(df, MAX_FEATURES)
    print("Text vectorization completed.")  #checking
    X_temp, X_test, y_temp, y_test = train_test_split(tfidf_matrix, labels, test_size=TEST_SIZE,
                                                      random_state=RANDOM_STATE)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=VALIDATION_SIZE,
                                                      random_state=RANDOM_STATE)
    print("Data split into training, validation, and test sets.")  #checking

    model = train_model(X_train, y_train)
    print("Model training completed.")  #checking
    results = evaluate_model(model, X_train, y_train, X_val, y_val, X_test, y_test)
    print(results)

    # Save the model and vectorizer to disk
    dump(model, 'svm_model.joblib')
    dump(vectorizer, 'tfidf_vectorizer.joblib')
    print("Model and vectorizer have been saved.")  #checking


if __name__ == "__main__":
    main()
