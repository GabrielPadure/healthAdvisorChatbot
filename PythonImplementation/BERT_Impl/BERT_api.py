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

def load_datasets(file_paths):
    data = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            loaded_data = json.load(f)
            data.extend(loaded_data)
    return data

dataset_files = [
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/Resources/CleanData/WithContext/Fitness.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/Resources/CleanData/WithContext/Med&Suppl.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/Resources/CleanData/WithContext/MentalHealth.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/Resources/CleanData/WithContext/Nutr&Diet.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/Resources/CleanData/WithContext/Symp&Cond.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/Resources/CleanData/WithContext/Non_health_related.json',
    "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/Resources/CleanData/WithContext/exercisesURL1.json"
]

qa_data = load_datasets(dataset_files)
vectorizer = TfidfVectorizer().fit([item['question'] for item in qa_data])
spell = SpellChecker()

svm_model = joblib.load('/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/SVM/svm_classifier.pkl')
vectorizer = joblib.load('/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/SVM/tfidf_vectorizer.pkl')

def retrieve_context(question, threshold, previous_suggestions):
    question_lower = question.lower()
    question_vec = vectorizer.transform([question_lower])
    dataset_vecs = vectorizer.transform([item['question'].lower() for item in qa_data])
    similarities = cosine_similarity(question_vec, dataset_vecs).flatten()

    sorted_indices = similarities.argsort()[::-1]
    for index in sorted_indices:
        if similarities[index] < threshold:
            break
        if qa_data[index]['question'].lower() not in previous_suggestions:
            if 'answer' in qa_data[index]:
                return qa_data[index]['answer'], qa_data[index]['question'], qa_data[index].get('videoURL'), similarities[index]

    return None, None, None, None

def load_model_and_tokenizer(model_path, tokenizer_path):
    model = BertForQuestionAnswering.from_pretrained(model_path)
    tokenizer = BertTokenizerFast.from_pretrained(tokenizer_path)
    return model, tokenizer

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

    return answer

def generate_gpt_neo_response(model, tokenizer, question):
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    inputs = tokenizer.encode_plus(question, return_tensors='pt', padding=True)
    input_ids = inputs['input_ids'].to(model.device)
    attention_mask = inputs['attention_mask'].to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=50,
            num_return_sequences=1,
            temperature=0.9,
            top_p=0.8,
            no_repeat_ngram_size=2,
            pad_token_id=tokenizer.eos_token_id
        )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    lines = generated_text.split('\n')
    cleaned_lines = [line for line in lines if question.lower() not in line.lower()]
    cleaned_text = ' '.join(cleaned_lines).strip()

    return cleaned_text

def classify_question(question):
    question_vec = vectorizer.transform([question])
    label = svm_model.predict(question_vec)[0]
    return label

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_path = '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/BERT_Impl/fine_tuned_bert_qa'
tokenizer_path = '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/BERT_Impl/fine_tuned_bert_qa'

start_time = time.time()
print("Loading BERT model...")
model, tokenizer = load_model_and_tokenizer(model_path, tokenizer_path)
model.to(device)
print(f"BERT model loaded in {time.time() - start_time:.2f} seconds.")

start_time = time.time()
print("Loading GPT-Neo 125M model...")
gpt_neo_model = GPTNeoForCausalLM.from_pretrained('EleutherAI/gpt-neo-125M')
gpt_neo_tokenizer = GPT2Tokenizer.from_pretrained('EleutherAI/gpt-neo-125M')
gpt_neo_model.to(device)
print(f"GPT-Neo 125M model loaded in {time.time() - start_time:.2f} seconds.")

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question').lower()
    initial_threshold = data.get('threshold', 0.7)
    previous_suggestions = [suggestion.lower() for suggestion in data.get('previous_suggestions', [])]
    confirm = data.get('confirm', False)
    matched_question = data.get('matched_question')
    context = data.get('context')
    video_url = data.get('videoURL')
    found_match = False
    threshold = initial_threshold

    corrected_question = correct_spelling(question)
    print(corrected_question)

    if confirm and context:
        return jsonify({
            "answer": context,
            "videoURL": video_url
        })

    label = classify_question(corrected_question)
    print(f"Classified label: {label}")

    if label == "Other":
        return jsonify({"answer": "I'm sorry, I can only answer health-related questions. Please ask something related to health, fitness, diet, or medicine.", "found_match": False})

    if label not in ["Fitness", "Medication & Supplements", "Mental Health", "Nutrition & Diet", "Symptoms & Conditions", "Exercises"]:
        return jsonify({"answer": "I am designed to answer health-related questions. Please ask something related to health, fitness, diet, or medicine.", "found_match": False})

    while threshold >= 0.5:
        context, matched_question, video_url, score = retrieve_context(corrected_question, threshold, previous_suggestions)
        print(f"Context: {context}, Matched Question: {matched_question}, Video URL: {video_url}, Score: {score}, Threshold: {threshold}")

        if context is not None:
            found_match = True
            response_data = {
                "matched_question": matched_question,
                "context": context,
                "score": score,
                "found_match": found_match,
                "label": label,
                "videoURL": video_url
            }

            if matched_question.lower() == corrected_question.lower():
                print(f"Exact match found at threshold {threshold}")
                return jsonify(response_data)
            else:
                print(f"Match found at threshold {threshold}")
                return jsonify(response_data)

        threshold -= 0.05

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
            corrected_word = word
        corrected_words.append(corrected_word)
    return ' '.join(corrected_words)

if __name__ == '__main__':
    app.run(port=5001)
