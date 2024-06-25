import json
import random
import pandas as pd

def generate_context(question, answer):
    templates = [
        f"The answer to the question '{question}' is '{answer}'.",
        f"When asked '{question}', the response is '{answer}'.",
        f"'{answer}' is the answer to '{question}'.",
        f"If you want to know '{question}', the answer is '{answer}'.",
        f"To the question '{question}', one should reply with '{answer}'."
    ]
    return random.choice(templates)

def transform_excel(input_excel_file, output_json_file, label):
    # Load Excel file
    df = pd.read_excel(input_excel_file)

    # Transform data
    transformed_data = []
    for index, row in df.iterrows():
        question = row[0]
        answer = row[1]
        videoURL = row[2] if len(row) > 2 else ''

        # Ensure answer is a string and remove brackets if present
        if isinstance(answer, str) and (answer.startswith('[') and answer.endswith(']')):
            answer = ' '.join(eval(answer))

        context = generate_context(question, answer)
        transformed_data.append({
            "label": label,
            "question": question,
            "context": context,
            "answer": answer,

        })

    # Write to JSON file
    with open(output_json_file, 'w') as f:
        json.dump(transformed_data, f, indent=4)

    print("Dataset transformation complete.")

# Example usage
input_excel_file = '/PythonImplementation/Resources/CleanData/WithContext/Symp.xlsx'
output_json_file = '/PythonImplementation/Resources/CleanData/WithContext/Symp.json'
label = 'Symptoms & Conditions'  # Change this to the appropriate label

transform_excel(input_excel_file, output_json_file, label)
