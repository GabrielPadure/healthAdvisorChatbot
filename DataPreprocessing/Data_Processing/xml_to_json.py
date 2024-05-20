import xml.etree.ElementTree as ET
import json

def extract_to_json(xml_file_path, json_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    data = []
    for record in root.findall('record'):
        question = record.find('question').text
        answer_element = record.find('answer')
        if answer_element is not None:
            snips = answer_element.findall('snip')
            if snips:
                first_snip = snips[0]
                answer_text = first_snip.find('sniptext').text if first_snip.find('sniptext') is not None else ""
                answer = answer_text
            else:
                answer = ""
        else:
            answer = ""

        data.append({
            'question': question,
            'answer': answer
        })

    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Example usage:
xml_file_path = '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/ClinicalInquiries.xml'
json_file_path = '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/ClinicalInquiries.json'
extract_to_json(xml_file_path, json_file_path)
