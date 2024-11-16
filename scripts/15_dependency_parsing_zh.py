"""
Script Name: 15_dependency_parsing_zh.py
Description:
    - This script processes Chinese language responses from XML files using spaCy's 'zh_core_web_lg' model to perform dependency parsing. It annotates each word with its part-of-speech, dependency tag, and the dependency distance to its syntactic head. The annotated responses are then saved into new XML files in a specified output directory. Non-Chinese tokens are tagged with a custom tag "NON-ZH".
    - Supports two modes:
        1. Process 20 separate files: Each XML files contain 100 responses, which are generated with the same prompt. 
        2. Process 2 merged files: Each XML files contain 1000 responses, which are merged according to the same prompt type and response type. 
"""

import spacy
from spacy.tokens import Token
from spacy.language import Language
import re
from lxml import etree
import os

# Load the spaCy Chinese model. 
nlp = spacy.load("zh_core_web_lg")

# Register extension attributes. 
Token.set_extension("is_non_chinese", default=False, force=True)
Token.set_extension('custom_pos', default=None, force=True)  # Add custom pos. 
Token.set_extension("custom_tag", default=None, force=True)  # Add custom tags. 

# Define a custom component for marking non-Chinese characters. 
@Language.component("detect_non_chinese")
def detect_non_chinese(doc):
    # Regular expression that matches strings with no Chinese characters, allowing digits. 
    non_chinese_pattern = re.compile(r'^[^\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\d]+$')
    for token in doc:
        # Mark the token as non-Chinese if it fits the pattern and is not just a number. 
        if non_chinese_pattern.match(token.text):
            token._.is_non_chinese = True
            token._.custom_pos = "NON-ZH"
            token._.custom_tag = "NON-ZH"
        else:
            token._.is_non_chinese = False
    return doc

# Add the custom component to the pipeline after the parser. 
nlp.add_pipe("detect_non_chinese", after="parser")

def dependency_parsing(input_dir, output_dir_general, output_dir_specific):
    # Ensure both output directories exist.
    if not os.path.exists(output_dir_general):
        os.makedirs(output_dir_general)
    if not os.path.exists(output_dir_specific):
        os.makedirs(output_dir_specific)

    # Iterate through all files in the specified input folder. 
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.xml'):  # Ensure only XML files are processed. 
            input_file_path = os.path.join(input_dir, file_name)
            tree = etree.parse(input_file_path)
            root = tree.getroot()
            responses = root.findall('response')
            total_responses = len(responses)  # Get the total number of responses for progress tracking. 

            for index, response in enumerate(responses):
                text = response.text.strip() if response.text else ""
                response.text = None  # Clear the original text of the response. 

                doc = nlp(text)
                
                sentence_id = 1
                for sent in doc.sents:
                    s_elem = etree.SubElement(response, 's', id=f"{response.get('id')}-s{sentence_id}")
                    token_id = 1
                    for token in sent:
                        # Calculate the dependency distance. 
                        dep_distance = abs(token.i - token.head.i)  # Dependency distance is the absolute index difference between the token and its head. 

                        t_id = f"{s_elem.get('id')}-t{token_id}"
                        # Create a word element with POS, dependency relation, and dependency distance. There is no lemma in Chinese, so 'token.lemma_' is not included in the output. 
                        t_elem = etree.SubElement(
                            s_elem, 't',
                            id=t_id, pos=token.pos_ if not token._.is_non_chinese else token._.custom_pos, tag=token.tag_ if not token._.is_non_chinese else token._.custom_tag, 
                            dep=token.dep_, head=token.head.text, dep_distance=str(dep_distance)
                        )
                        t_elem.text = token.text
                        token_id += 1
                    sentence_id += 1

                # Print progress information. 
                print(f"Processed {index + 1}/{total_responses} responses in {file_name}.")

            # Indent to improve the formatting of the output XML file. 
            etree.indent(root, space="  ", level=0)

            # Define the output file names with "dependency_parsing_" prefix.
            output_file_name = f"dependency_parsing_{file_name}"
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
    ('../data/raw_data/response_list/separate/zh', '../data/processed_data/dependency/dependency_parsing/separate/all', '../data/processed_data/dependency/dependency_parsing/separate/zh'),
    
    # Process 2 merged fileswith 1000 responses each. 
    ('../data/raw_data/response_list/merged/zh', '../data/processed_data/dependency/dependency_parsing/merged/all', '../data/processed_data/dependency/dependency_parsing/merged/zh')
]

# Execute the dependency parsing for all configurations.
for input_dir, output_dir_general, output_dir_specific in configurations:
    print(f"Starting dependency parsing for files in {input_dir}...")
    dependency_parsing(input_dir, output_dir_general, output_dir_specific)
    print(f"All files in {input_dir} have been processed and saved to both directories.")