import json
import joblib
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Load the saved model and vectorizer
svm_model = joblib.load('/PythonImplementation/SVM/svm_classifier.pkl')
vectorizer = joblib.load('/PythonImplementation/SVM/tfidf_vectorizer.pkl')

# Load health-related dataset for testing
health_test_files = [
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Fitness.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Med&Suppl.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/MentalHealth.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Nutr&Diet.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Symp&Cond.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/exercisesURL1.json'
]

health_test_data = []
for file_path in health_test_files:
    with open(file_path, 'r') as f:
        health_test_data.extend(json.load(f))

# Load non-health-related dataset for testing
with open('/PythonImplementation/Resources/CleanData/WithContext/Non_health_related.json', 'r') as f:
    non_health_test_data = json.load(f)

# Combine datasets
combined_test_data = health_test_data + non_health_test_data

# Extract questions and labels
test_questions = [item['question'] for item in combined_test_data]
test_labels = [item['label'] for item in combined_test_data]

# Vectorize the test questions
X_test_vec = vectorizer.transform(test_questions)

# Predict using the loaded model
y_pred = svm_model.predict(X_test_vec)

# Evaluate the model
accuracy = accuracy_score(test_labels, y_pred)
print(f"Model accuracy: {accuracy:.2f}")

# Print classification report
print("Classification Report:")
print(classification_report(test_labels, y_pred))

# Print confusion matrix
print("Confusion Matrix:")
print(confusion_matrix(test_labels, y_pred))
