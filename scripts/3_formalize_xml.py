"""
Script Name: 3_formalize_xml.py

Description:
    - This script processes 40 XML files, updating their structure and saving new files in two locations. The files are saved both in a general directory and a response-type-specific directory for easier subsequent processing. 
    - The script assigns new ids to responses based on their sequence within their respective prompt, and sets attributes for prompt and response languages. 
    - It maintains the original content of responses but updates the attributes and excluded the prompt contents in updated files.
    
Attributes:
    - prompt_type: Language of the prompt (e.g., 'en' for English, 'zh' for Chinese).
    - response_type: Language of the responses (e.g., 'en' for English, 'zh' for Chinese).
"""

from lxml import etree
import os

def formalize_xml_files(input_dir, output_dir, file_prefix, prompt_type, response_type):
    # Define paths for general and response-type-specific output folders.
    output_dir_general = os.path.join(output_dir, "all")
    output_dir_specific = os.path.join(output_dir, response_type)
    
    # Ensure both directories exist.
    if not os.path.exists(output_dir_general):
        os.makedirs(output_dir_general)
    if not os.path.exists(output_dir_specific):
        os.makedirs(output_dir_specific)

    # Process each XML file, updating structure and saving in two locations.
    for i in range(1, 11):
        file_name = f'{file_prefix}{i}.xml'
        input_file = os.path.join(input_dir, file_name)
        # Path to store the overall 40 output files. 
        output_file_general = os.path.join(output_dir_general, file_name)  
        # Path to the folders according to the response type, i.e. English responses and Chinese responses are stored separately. 
        output_file_specific = os.path.join(output_dir_specific, file_name) 
        
        tree = etree.parse(input_file)
        root = tree.getroot()
        
        # Update prompt and response types in the XML structure.
        root.set('prompt_type', prompt_type)
        root.set('response_type', response_type)

        # Add newline and indentation for proper formatting.
        root.text = "\n  "

        # Remove prompt contents. 
        prompt_content = root.find('prompt_content')
        if prompt_content is not None:
            root.remove(prompt_content)

        # Set new IDs for each response, and preserve their content.
        for j, response in enumerate(root.findall('.//response'), start=1):
            # p1 to p10 represent prompts and r1 to r 100 stand for responses
            new_id = f'p{i}-r{j}'
            response.set('id', new_id)

            # Strip leading and trailing whitespace from response text.
            if response.text:
                response.text = response.text.strip()
                
        # Write the updated XML files to both specified directories.
        tree.write(output_file_general, pretty_print=True, xml_declaration=True, encoding='utf-8')
        tree.write(output_file_specific, pretty_print=True, xml_declaration=True, encoding='utf-8')
    
    print(f'Completed updating files with prefix {file_prefix}. Saved in both general and specific directories.')

# Configuration setup for different language combinations.
configurations = [
    ('../data/raw_data/raw_response', '../data/raw_data/response_list/separate', 'response_en_en_', 'en', 'en'),
    ('../data/raw_data/raw_response', '../data/raw_data/response_list/separate', 'response_zh_en_', 'zh', 'en'),
    ('../data/raw_data/raw_response', '../data/raw_data/response_list/separate', 'response_en_zh_', 'en', 'zh'),
    ('../data/raw_data/raw_response', '../data/raw_data/response_list/separate', 'response_zh_zh_', 'zh', 'zh')
]

# Execute the formalization process for all specified configurations.
for input_dir, output_dir, file_prefix, prompt_type, response_type in configurations:
    formalize_xml_files(input_dir, output_dir, file_prefix, prompt_type, response_type)
    print(f'All files with prefix {file_prefix} have been processed and saved to {output_dir} and {output_dir}/{response_type}.')
