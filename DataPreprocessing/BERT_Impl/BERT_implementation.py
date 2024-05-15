import json
import torch
from transformers import BertTokenizer, BertForQuestionAnswering
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Load your datasets
def load_datasets(file_paths):
    data = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            data.extend(json.load(f))
    return data

# Example dataset files (update these paths as needed)
dataset_files = [
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/Fitness.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/MentalHealth.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/Symp&Cond.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/Med&Suppl.json',
    '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/Nutr&Diet.json'
]

qa_data = load_datasets(dataset_files)

# Prepare TF-IDF vectorizer and fit on the questions
vectorizer = TfidfVectorizer().fit([item['question'] for item in qa_data])

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
    tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
    return model, tokenizer

def clean_answer(answer):
    if '?' in answer:
        answer = answer.split('?')[1]  # Remove everything before the '?'
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

    # Clean up the answer tokens
    answer = answer.replace('[CLS]', '').replace('[SEP]', '').replace('[PAD]', '').strip()
    answer = ' '.join(answer.split())  # remove extra spaces
    answer = clean_answer(answer)  # Remove text before '?'

    return answer

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_path = 'fine_tuned_bert_qa'
    tokenizer_path = 'fine_tuned_bert_qa'

    model, tokenizer = load_model_and_tokenizer(model_path, tokenizer_path)
    model.to(device)

    while True:
        question = input("Question: ")
        if question.lower() in ['exit', 'quit']:
            break

        threshold = 0.7
        found_match = False

        while threshold >= 0.5:
            print(f"Searching for a match with threshold: {threshold}")
            context, matched_question, score = retrieve_context(question, threshold)
            if context is not None:
                found_match = True
                print(f"Did you mean: '{matched_question}'? (yes/no)")
                user_response = input().strip().lower()
                if user_response == 'yes':
                    print(f"Matched Question: {matched_question}")
                    print(f"Context: {context}")
                    answer = answer_question(model, tokenizer, question, context, device)
                    print(f"Answer: {answer}")
                    break
                else:
                    threshold -= 0.05
                    found_match = False
            else:
                threshold -= 0.05

        if not found_match:
            print("Sorry, I couldn't find a good match for your question.")

if __name__ == '__main__':
    main()
