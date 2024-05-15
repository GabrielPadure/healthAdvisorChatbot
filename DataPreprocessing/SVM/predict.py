from flask import Flask, request, jsonify
from flask_cors import CORS
from joblib import load

from DataPreprocessing.Data_Processing.text_cleaning_impl import preprocess_text

app = Flask(__name__)
CORS(app)
model = load('svm_model.joblib')
vectorizer = load('tfidf_vectorizer.joblib')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    raw_text = data['text']
    cleaned_text = preprocess_text(raw_text)
    text_tfidf = vectorizer.transform([cleaned_text])
    prediction = model.predict(text_tfidf)
    # Add cleaned text to the response for debugging
    return jsonify({'category': prediction[0], 'cleaned_text': cleaned_text})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
