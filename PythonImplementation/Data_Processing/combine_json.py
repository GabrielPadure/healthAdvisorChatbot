import json


def combine_json_files(input_file1, input_file2, output_file):
    # Read the first JSON file
    with open(input_file1, 'r') as f1:
        data1 = json.load(f1)

    # Read the second JSON file
    with open(input_file2, 'r') as f2:
        data2 = json.load(f2)

    # Combine the data from both files
    combined_data = data1 + data2

    # Write the combined data to the output JSON file
    with open(output_file, 'w') as f_out:
        json.dump(combined_data, f_out, indent=4)

    print(f"Combined {input_file1} and {input_file2} into {output_file}")


# Example usage
input_file1 = '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/'
input_file2 = '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/'
output_file = '/PythonImplementation/Resources/CleanData/WithContext/'

combine_json_files(input_file1, input_file2, output_file)
