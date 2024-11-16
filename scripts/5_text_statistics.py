"""
Script Name: 5_text_statistics.py
Description:
    - Analyzes XML files to count the number of words, tokens, and sentences in each response using spaCy.
    - Uses the 'en_core_web_lg' model for English and 'zh_core_web_lg' for Chinese text.
    - Outputs annotated XML files and JSON statistics files to two specified output directories with a prefix "text_statistics_".
"""

import spacy
from lxml import etree
import os
import json

# Load spaCy large models for English and Chinese processing.
nlp_en = spacy.load("en_core_web_lg")
nlp_zh = spacy.load("zh_core_web_lg") 

def count_statistics(input_dir, output_dir_general, output_dir_specific):
    # Ensure both output directories exist.
    os.makedirs(output_dir_general, exist_ok=True)
    os.makedirs(output_dir_specific, exist_ok=True)

    # Get all the xml files in the input directory. 
    file_list = sorted([file_name for file_name in os.listdir(input_dir) if file_name.endswith('.xml')])

    # Process each XML file in the list.
    for file_name in file_list:
        input_xml_path = os.path.join(input_dir, file_name)

        # Add "text_statistics_" prefix to the output file names.
        output_file_name = f"text_statistics_{file_name}"
        output_xml_path_general = os.path.join(output_dir_general, output_file_name)
        output_xml_path_specific = os.path.join(output_dir_specific, output_file_name)
        output_json_path_general = os.path.join(output_dir_general, output_file_name.replace('.xml', '.json'))
        output_json_path_specific = os.path.join(output_dir_specific, output_file_name.replace('.xml', '.json'))

        print(f"Processing file: {file_name}...")

        tree = etree.parse(input_xml_path)
        root = tree.getroot()
        response_type = root.get('response_type')

        # Choose the appropriate spaCy model based on the response type.
        nlp = nlp_en if response_type == 'en' else nlp_zh

        responses_data = []  # List to store response statistics.

        # Analyze each response for text statistics.
        for j, response in enumerate(root.findall('.//response'), 1):
            text = response.text 
            doc = nlp(text)
            # Count the number of words in each response (punctuations and spaces are not included).
            word_count = len([token for token in doc if not token.is_punct and not token.is_space])
            # Count the number of tokens (punctuations are also inculded).
            token_count = len(doc)
            # Count the number of sentences.
            sentence_count = len(list(doc.sents))

            # Update the XML element with new statistics. 
            response.set('word_count', str(word_count))
            response.set('token_count', str(token_count))
            response.set('sentence_count', str(sentence_count))

            # Prepare data for JSON output. 
            response_data = {
                "id": response.get('id', f"default_id_{j}"),  # Use a default id if there is no id in input files
                "word_count": word_count,
                "token_count": token_count,
                "sentence_count": sentence_count
            }
            responses_data.append(response_data)

            print(f"  Response {j}: {word_count} words, {token_count} tokens, {sentence_count} sentences.")

        # Write the updated XML file to both directories.
        tree.write(output_xml_path_general, pretty_print=True, xml_declaration=True, encoding='utf-8')
        tree.write(output_xml_path_specific, pretty_print=True, xml_declaration=True, encoding='utf-8')
        print(f"Completed writing XML to {output_xml_path_general} and {output_xml_path_specific}.")

        # Write response statistics to JSON files in both directories.
        with open(output_json_path_general, 'w', encoding='utf-8') as json_file:
            json.dump(responses_data, json_file, indent=4, ensure_ascii=False)
        with open(output_json_path_specific, 'w', encoding='utf-8') as json_file:
            json.dump(responses_data, json_file, indent=4, ensure_ascii=False)
        print(f"Completed writing JSON to {output_json_path_general} and {output_json_path_specific}.")

# Configuration setup for folder and file processing.
configurations = [
    # Separate files mode.
    ('../data/raw_data/response_list/separate/en', '../data/processed_data/text_statistics/separate/all', '../data/processed_data/text_statistics/separate/en'),
    ('../data/raw_data/response_list/separate/zh', '../data/processed_data/text_statistics/separate/all', '../data/processed_data/text_statistics/separate/zh'),

    # Merged files mode.
    ('../data/raw_data/response_list/merged/en', '../data/processed_data/text_statistics/merged/all', '../data/processed_data/text_statistics/merged/en'),
    ('../data/raw_data/response_list/merged/zh', '../data/processed_data/text_statistics/merged/all', '../data/processed_data/text_statistics/merged/zh')
]

# Execute the processing for all configurations.
for input_dir, output_dir_general, output_dir_specific in configurations:
    print(f"Starting to process XML files in directory {input_dir}...")
    count_statistics(input_dir, output_dir_general, output_dir_specific)
    print(f"All files in {input_dir} have been processed and saved to both directories.")
