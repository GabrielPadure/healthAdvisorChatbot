import json
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
import joblib

# Load health-related dataset
health_related_files = [
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Fitness.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Med&Suppl.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/MentalHealth.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Nutr&Diet.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Symp&Cond.json',

]

health_data = []
for file_path in health_related_files:
    with open(file_path, 'r') as f:
        health_data.extend(json.load(f))

# Load non-health-related dataset
with open('/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Non_health_related.json', 'r') as f:
    non_health_data = json.load(f)

# Combine datasets
combined_data = health_data + non_health_data

# Extract questions and labels
questions = [item['question'] for item in combined_data]
labels = [item['label'] for item in combined_data]

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(questions, labels, test_size=0.2, random_state=42)

# Vectorize the questions
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train the SVM model
svm_model = SVC(kernel='linear', probability=True)
svm_model.fit(X_train_vec, y_train)

# Evaluate the model
accuracy = svm_model.score(X_test_vec, y_test)
print(f"Model accuracy: {accuracy:.2f}")

# Save the model and vectorizer
joblib.dump(svm_model, '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/SVM/svm_classifier.pkl')
joblib.dump(vectorizer, '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/SVM/tfidf_vectorizer.pkl')
