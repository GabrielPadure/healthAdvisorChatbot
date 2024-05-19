from flask import Flask, request, jsonify
from flask_cors import CORS
from joblib import load
from spellchecker import SpellChecker

from DataPreprocessing.Data_Processing.text_cleaning_impl import preprocess_text

app = Flask(__name__)
CORS(app)

# Load the model and vectorizer
model = load('DataPreprocessing/SVM/svm_model.joblib')
vectorizer = load('DataPreprocessing/SVM/tfidf_vectorizer.joblib')

# Initialize the spell checker
spell = SpellChecker()

def correct_spelling(text):
    corrected_text = []
    for word in text.split():
        corrected_word = spell.correction(word)
        corrected_text.append(corrected_word)
    return ' '.join(corrected_text)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        raw_text = data['text']
        print(raw_text)
        # Correct the spelling of the raw text
        corrected_text = correct_spelling(raw_text)
        print(corrected_text)
        
        # Preprocess the corrected text
        cleaned_text = preprocess_text(corrected_text)
        
        # Vectorize the cleaned text
        text_tfidf = vectorizer.transform([cleaned_text])
        
        # Predict the category
        prediction = model.predict(text_tfidf)
        
        # Return the prediction, cleaned text, and corrected text
        return jsonify({
            'category': prediction[0],
            'cleaned_text': cleaned_text,
            'corrected_text': corrected_text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)