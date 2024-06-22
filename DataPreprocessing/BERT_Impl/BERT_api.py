from flask import Flask, request, jsonify
import json
import torch
from spellchecker import SpellChecker
from transformers import BertTokenizerFast, BertForQuestionAnswering, GPT2LMHeadModel, GPT2Tokenizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer



app = Flask(__name__)

def load_datasets(file_paths):
    data = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            data.extend(json.load(f))
    return data

dataset_files = [
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Fitness.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Med&Suppl.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/MentalHealth.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Nutr&Diet.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Symp&Cond.json'
]

qa_data = load_datasets(dataset_files)
vectorizer = TfidfVectorizer().fit([item['question'] for item in qa_data])
spell = SpellChecker()

def retrieve_context(question, threshold):
    question_vec = vectorizer.transform([question])
    dataset_vecs = vectorizer.transform([item['question'] for item in qa_data])
    similarities = cosine_similarity(question_vec, dataset_vecs).flatten()

    best_match_index = similarities.argmax()
    best_match_score = similarities[best_match_index]

    if best_match_score < threshold:
        return None, None, best_match_score

    best_match = qa_data[best_match_index]
    return best_match['answer'], best_match['question'], best_match_score

def load_model_and_tokenizer(model_path, tokenizer_path):
    model = BertForQuestionAnswering.from_pretrained(model_path)
    tokenizer = BertTokenizerFast.from_pretrained(tokenizer_path)
    return model, tokenizer

def clean_answer(answer):
    if '?' in answer:
        answer = answer.split('?')[1]
    return answer.strip()

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

def generate_gpt2_answer(model, tokenizer, question):
    input_ids = tokenizer.encode(question + '', return_tensors='pt').to(model.device)
    with torch.no_grad():
        outputs = model.generate(input_ids, max_length=50, num_return_sequences=1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_path = 'fine_tuned_bert_qa'
tokenizer_path = 'fine_tuned_bert_qa'

model, tokenizer = load_model_and_tokenizer(model_path, tokenizer_path)
model.to(device)

# Load GPT-2 model and tokenizer
gpt2_model = GPT2LMHeadModel.from_pretrained('gpt2')
gpt2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
gpt2_model.to(device)

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')
    threshold = data.get('threshold', 0.7)
    found_match = False

    # Correct the spelling mistakes in the question
    corrected_question = correct_spelling(question)

    context, matched_question, score = retrieve_context(corrected_question, threshold)
    if context is not None:
        found_match = True
        return jsonify(
            {"matched_question": matched_question, "context": context, "score": score, "found_match": found_match})

    if not found_match:
        answer = generate_gpt2_answer(gpt2_model, gpt2_tokenizer, corrected_question)
        return jsonify({"answer": answer, "found_match": found_match})

@app.route('/get_answer', methods=['POST'])
def get_answer():
    data = request.json
    question = data.get('question')
    context = data.get('context')

    answer = answer_question(model, tokenizer, question, context, device)
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
    app.run(port=5000)
