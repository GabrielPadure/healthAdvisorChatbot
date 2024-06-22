from flask import Flask, request, jsonify
import json
import torch
import joblib
from spellchecker import SpellChecker
from transformers import BertTokenizerFast, BertForQuestionAnswering, GPTNeoForCausalLM, GPT2Tokenizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import time

app = Flask(__name__)

# Function to load datasets
def load_datasets(file_paths):
    data = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            loaded_data = json.load(f)
            print(f"Loaded data from {file_path}: {loaded_data[:1]}")  # Print only the first item for brevity
            data.extend(loaded_data)
    return data

# File paths for datasets
dataset_files = [
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Fitness.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Med&Suppl.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/MentalHealth.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Nutr&Diet.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Symp&Cond.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Non_health_related.json'  # Include a file for non-health-related questions
]

qa_data = load_datasets(dataset_files)
vectorizer = TfidfVectorizer().fit([item['question'] for item in qa_data])
spell = SpellChecker()

# Load the trained SVM model and vectorizer
svm_model = joblib.load('/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/SVM/svm_classifier.pkl')
vectorizer = joblib.load('/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/SVM/tfidf_vectorizer.pkl')

# Function to retrieve context
def retrieve_context(question, threshold, previous_suggestions):
    question_vec = vectorizer.transform([question])
    dataset_vecs = vectorizer.transform([item['question'] for item in qa_data])
    similarities = cosine_similarity(question_vec, dataset_vecs).flatten()

    sorted_indices = similarities.argsort()[::-1]
    for index in sorted_indices:
        if similarities[index] < threshold:
            break
        if qa_data[index]['question'] not in previous_suggestions:
            if 'answer' in qa_data[index]:  # Check if 'answer' key exists
                print(f"Matched question: {qa_data[index]['question']}, Score: {similarities[index]}, Threshold: {threshold}")  # Debug statement
                return qa_data[index]['answer'], qa_data[index]['question'], similarities[index]
            else:
                print(f"Missing 'answer' key in entry: {qa_data[index]}")

    return None, None, None

# Function to load model and tokenizer
def load_model_and_tokenizer(model_path, tokenizer_path):
    model = BertForQuestionAnswering.from_pretrained(model_path)
    tokenizer = BertTokenizerFast.from_pretrained(tokenizer_path)
    return model, tokenizer

# Function to clean answer
def clean_answer(answer):
    if '?' in answer:
        answer = answer.split('?')[1]
    return answer.strip()

# Function to get answer from BERT model
def answer_question(model, tokenizer, question, context, device):
    inputs = tokenizer.encode_plus(
        question, context,
        add_special_tokens=True,
        max_length=512,
        truncation=True,
        padding='max_length',
        return_tensors='pt'
    )

    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        start_scores = outputs.start_logits
        end_scores = outputs.end_logits

    start_index = torch.argmax(start_scores)
    end_index = torch.argmax(end_scores) + 1

    all_tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
    answer_tokens = all_tokens[start_index:end_index]
    answer = tokenizer.convert_tokens_to_string(answer_tokens)

    answer = answer.replace('[CLS]', '').replace('[SEP]', '').replace('[PAD]', '').strip()
    answer = ' '.join(answer.split())
    answer = clean_answer(answer)

    return answer

# Function to generate answer using GPT-Neo 125M
def generate_gpt_neo_response(model, tokenizer, question):
    # Set pad_token to eos_token if not already set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Tokenize the input question
    inputs = tokenizer.encode_plus(question, return_tensors='pt', padding=True)
    input_ids = inputs['input_ids'].to(model.device)
    attention_mask = inputs['attention_mask'].to(model.device)

    # Generate the output from the model
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=50,  # Shorten the response length
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            no_repeat_ngram_size=2,
            pad_token_id=tokenizer.eos_token_id
        )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Post-process the generated text to clean up the response
    # Remove any lines that repeat the question verbatim
    lines = generated_text.split('\n')
    cleaned_lines = [line for line in lines if question.lower() not in line.lower()]
    cleaned_text = ' '.join(cleaned_lines).strip()

    # Ensure the response is coherent and short
    if len(cleaned_text.split()) > 30:
        cleaned_text = ' '.join(cleaned_text.split()[:30]) + '...'

    return cleaned_text

# Function to classify the question
def classify_question(question):
    question_vec = vectorizer.transform([question])  # Transform the question
    label = svm_model.predict(question_vec)[0]
    return label

# Load models and tokenizers at the start of the application
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_path = 'fine_tuned_bert_qa'
tokenizer_path = 'fine_tuned_bert_qa'

# Add logging for model loading
start_time = time.time()
print("Loading BERT model...")
model, tokenizer = load_model_and_tokenizer(model_path, tokenizer_path)
model.to(device)
print(f"BERT model loaded in {time.time() - start_time:.2f} seconds.")

# Load GPT-Neo 125M model and tokenizer
start_time = time.time()
print("Loading GPT-Neo 125M model...")
gpt_neo_model = GPTNeoForCausalLM.from_pretrained('EleutherAI/gpt-neo-125M')
gpt_neo_tokenizer = GPT2Tokenizer.from_pretrained('EleutherAI/gpt-neo-125M')
gpt_neo_model.to(device)
print(f"GPT-Neo 125M model loaded in {time.time() - start_time:.2f} seconds.")

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')
    initial_threshold = data.get('threshold', 0.7)
    previous_suggestions = data.get('previous_suggestions', [])
    found_match = False
    threshold = initial_threshold

    # Correct the spelling mistakes in the question
    corrected_question = correct_spelling(question)
    print(corrected_question)

    # Classify the question
    label = classify_question(corrected_question)
    print(f"Classified label: {label}")  # Debug statement

    if label == "Other":
        return jsonify({"answer": "I'm sorry, I can only answer health-related questions. Please ask something related to health, fitness, diet, or medicine.", "found_match": False})

    if label not in ["Fitness", "Medication & Supplements", "Mental Health", "Nutrition & Diet", "Symptoms & Conditions"]:
        return jsonify({"answer": "I am designed to answer health-related questions. Please ask something related to health, fitness, diet, or medicine.", "found_match": False})

    while threshold >= 0.5:
        context, matched_question, score = retrieve_context(corrected_question, threshold, previous_suggestions)
        print(f"Context: {context}, Matched Question: {matched_question}, Score: {score}, Threshold: {threshold}")  # Debug statement

        if context is not None:
            # If a match is found
            found_match = True
            if matched_question.lower() == corrected_question.lower():
                # If the matched question is exactly the same as the asked question
                print(f"Exact match found at threshold {threshold}")
                return jsonify({"answer": context, "found_match": found_match})
            else:
                print(f"Match found at threshold {threshold}")
                return jsonify({"matched_question": matched_question, "context": context, "score": score, "found_match": found_match})

        threshold -= 0.05

    # If no match is found, use GPT-Neo to generate a response
    answer = generate_gpt_neo_response(gpt_neo_model, gpt_neo_tokenizer, corrected_question)
    return jsonify({"answer": answer, "found_match": found_match})

@app.route('/get_answer', methods=['POST'])
def get_answer():
    data = request.json
    question = data.get('question')
    context = data.get('context')

    answer = answer_question(model, tokenizer, question, context, device)
    return jsonify({"answer": answer})

@app.route('/generate_gpt_neo_response', methods=['POST'])
def generate_gpt_neo_response_endpoint():
    data = request.json
    question = data.get('question')
    answer = generate_gpt_neo_response(gpt_neo_model, gpt_neo_tokenizer, question)
    return jsonify({"answer": answer})

def correct_spelling(text):
    corrected_words = []
    for word in text.split():
        corrected_word = spell.correction(word)
        if corrected_word is None:
            corrected_word = word  # Use the original word if no correction is found
        corrected_words.append(corrected_word)
    return ' '.join(corrected_words)

if __name__ == '__main__':
    app.run(port=5001)
