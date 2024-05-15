import json

# Load the JSON file
file_path = '/DataPreprocessing/Resources/RawData/Symp&Cond.json'
with open(file_path, 'r') as file:
    data = json.load(file)

# Process the data: remove 'keywords' and add 'Fitness' as the first label
processed_data = []
for item in data:
    if 'keywords' in item:
        del item['keywords']
    new_item = {'label': 'Symptoms & Conditions'}
    new_item.update(item)
    processed_data.append(new_item)

# Save the processed data back to JSON
output_file_path = '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/Symp&Cond.json'
with open(output_file_path, 'w', encoding='utf-8') as file:
    json.dump(processed_data, file, ensure_ascii=False, indent=4)

print(f"Processed file saved to {output_file_path}")





