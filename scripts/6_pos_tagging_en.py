"""
Script Name: 6_pos_tagging_en.py
Description:
    - Conducts POS (Part-of-Speech) tagging on the text of English responses using spaCy's en_core_web_lg model.
    - Supports two modes:
        1. Process 20 separate files: Each XML files contain 100 responses, which are generated with the same prompt. 
        2. Process 2 merged files: Each XML files contain 1000 responses, which are merged according to the same prompt type and response type. 
    - Outputs the annotated XML files to two specified output directories for each mode, with the prefix 'pos_tagging_' added to the file names.
"""

import spacy
from lxml import etree
import os

# Load spaCy's large English model for POS tagging.
nlp = spacy.load("en_core_web_lg")

def pos_tagging(input_dir, output_dir_general, output_dir_specific):
    # Ensure both output directories exist.
    if not os.path.exists(output_dir_general):
        os.makedirs(output_dir_general)
    if not os.path.exists(output_dir_specific):
        os.makedirs(output_dir_specific)

    # Process each XML file in the input folder.
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.xml'):  # Ensure only XML files are processed.
            input_file_path = os.path.join(input_dir, file_name)
            tree = etree.parse(input_file_path)
            root = tree.getroot()
            responses = root.findall('response')
            total_responses = len(responses)  # Get the total number of responses for progress tracking.

            for index, response in enumerate(responses):
                text = response.text.strip() if response.text else ""
                response.text = None  # Clear the original text of the response

                doc = nlp(text)

                sentence_id = 1
                for sent in doc.sents:
                    s_elem = etree.SubElement(response, 's', id=f"{response.get('id')}-s{sentence_id}")
                    token_id = 1
                    for token in sent:
                        t_id = f"{s_elem.get('id')}-t{token_id}"
                        t_elem = etree.SubElement(s_elem, 't', id=t_id, lemma=token.lemma_, pos=token.pos_, tag=token.tag_)
                        t_elem.text = token.text
                        token_id += 1
                    sentence_id += 1

                # Print progress information.
                print(f"Processed {index + 1}/{total_responses} responses in {file_name}.")

            # Indent to improve the formatting of the output XML file.
            etree.indent(root, space="  ", level=0)

            # Define the output file names with "pos_tagging_" prefix.
            output_file_name = f"pos_tagging_{file_name}"
            output_file_path_general = os.path.join(output_dir_general, output_file_name)
            output_file_path_specific = os.path.join(output_dir_specific, output_file_name)

            # Write the output XML file to both directories.
            tree.write(output_file_path_general, pretty_print=True, xml_declaration=True, encoding='UTF-8')
            tree.write(output_file_path_specific, pretty_print=True, xml_declaration=True, encoding='UTF-8')

            print(f"Finished processing {input_file_path}, output saved to:")
            print(f"  - {output_file_path_general}")
            print(f"  - {output_file_path_specific}")

# Configuration setup for both standard and merged file processing.
configurations = [
    # Process 20 separate files with 100 responses each. 
    ('../data/raw_data/response_list/separate/en', '../data/processed_data/pos/pos_tagging/separate/all', '../data/processed_data/pos/pos_tagging/separate/en'),
    
    # Process 2 merged fileswith 1000 responses each. 
    ('../data/raw_data/response_list/merged/en', '../data/processed_data/pos/pos_tagging/merged/all', '../data/processed_data/pos/pos_tagging/merged/en')
]

# Execute the POS tagging for all configurations.
for input_dir, output_dir_general, output_dir_specific in configurations:
    print(f"Starting POS tagging for files in {input_dir}...")
    pos_tagging(input_dir, output_dir_general, output_dir_specific)
    print(f"All files in {input_dir} have been processed and saved to both directories.")
