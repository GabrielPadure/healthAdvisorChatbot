from flask import Flask, request, jsonify
from flask_cors import CORS
from joblib import load

app = Flask(__name__)
CORS(app)
model = load('svm_model.joblib')
vectorizer = load('tfidf_vectorizer.joblib')

# The route for prediction.
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data['text']
    # transform the text to a TF-IDF vector using the loaded vectorizer
    text_tfidf = vectorizer.transform([text])
    # predict the category
    prediction = model.predict(text_tfidf)
    # return the prediction
    return jsonify({'category': prediction[0]})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
