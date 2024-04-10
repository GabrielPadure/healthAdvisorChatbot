import pandas as pd

path_to_excel = 'Q&A Mental Health.xlsx'
# Load the Excel file without specifying encoding
data_excel = pd.read_excel(path_to_excel)

# Convert all columns to string type
for col in data_excel.columns:
    data_excel[col] = data_excel[col].astype(str)

# Save the DataFrame to a CSV file
data_excel.to_csv('mental_health.csv', index=None, header=True, encoding='utf-8-sig')
