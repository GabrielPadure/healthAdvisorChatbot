import pandas as pd

# Load the Excel file
file_path = '/PythonImplementation/Resources/CleanData/WithContext/exercisesURL.xlsx'
excel_data = pd.read_excel(file_path)

# Drop the 'id' column
excel_data = excel_data.drop(columns=['id'])

# Ensure the answer column does not have brackets
excel_data['answer'] = excel_data['answer'].apply(lambda x: ' '.join(eval(x)))

# Convert the dataframe to JSON format without changing the video URL format
json_data = excel_data.to_json(orient='records', indent=4)

# Define the output file path
output_file_path = '/PythonImplementation/Resources/CleanData/WithContext/exercisesURL.json'

# Save the JSON data to a file
with open(output_file_path, 'w') as json_file:
    json_file.write(json_data)

print(f'JSON file has been saved to {output_file_path}')
