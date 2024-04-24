import pandas as pd
from data_preprocessing import preprocess_question

# Read the CSV file
df = pd.read_csv('mental_health.csv')

# Apply preprocessing to extract keywords
df['Keywords'] = df['question'].apply(preprocess_question)

# Save the updated DataFrame to a new CSV file
df.to_csv('updated_file.csv', index=False)