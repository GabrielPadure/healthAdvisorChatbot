import json
import random

def generate_context(question, answer):
    templates = [
        f"The answer to the question '{question}' is '{answer}'.",
        f"When asked '{question}', the response is '{answer}'.",
        f"'{answer}' is the answer to '{question}'.",
        f"If you want to know '{question}', the answer is '{answer}'.",
        f"To the question '{question}', one should reply with '{answer}'."
    ]
    return random.choice(templates)

def transform_dataset(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    transformed_data = []
    for item in data:
        question = item['question']
        answer = item['answer']
        context = generate_context(question, answer)
        transformed_data.append({
            "label": item['label'],
            "question": question,
            "context": context,
            "answer": answer
        })

    with open(output_file, 'w') as f:
        json.dump(transformed_data, f, indent=4)

input_file = '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/Symp&Cond.json'
output_file = '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Symp&Cond.json'
transform_dataset(input_file, output_file)
print("Dataset transformation complete.")
