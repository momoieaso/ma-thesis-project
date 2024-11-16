"""
Script Name: 2_merge_xml.py
Description:
    - Merges 40 XML files into 4 XML files based on the same prompt type and response type, in order to make it easy for further processing. 
    - It saves each merged file in two different directories: one general directory for all files and another specific directory based on the response type.
    The script excludes prompt contents from the merged files.

Attributes:
    - prompt_type: The language of the prompt (e.g., 'en' for English, 'zh' for Chinese).
    - response_type: The language of the responses (e.g., 'en' for English, 'zh' for Chinese).
"""

from lxml import etree
import os

def merge_xml_files(input_dir, file_prefix, output_dir, output_file, prompt_type, response_type):
    # Define paths for the general and response-type-specific output folders.
    output_dir_general = os.path.join(output_dir, "all")
    output_dir_specific = os.path.join(output_dir, response_type)

    # Ensure both output directories exist, create them if not.
    if not os.path.exists(output_dir_general):
        os.makedirs(output_dir_general)
    if not os.path.exists(output_dir_specific):
        os.makedirs(output_dir_specific)

    # Create a new XML root element with prompt_type and response_type attributes.
    merged_root = etree.Element('responses', attrib={'prompt_type': prompt_type, 'response_type': response_type})

    # Add newline and indentation to align <response> elements properly.
    merged_root.text = "\n  "

    # Process each of the 10 XML files corresponding to the file prefix.
    for i in range(1, 11):
        input_file_name = f'{file_prefix}{i}.xml'
        input_path = os.path.join(input_dir, input_file_name) 

        print(f'Processing file: {input_path}')

        tree = etree.parse(input_path)
        input_root = tree.getroot()
        
        # Iterate over all response elements in each file, setting new IDs and preserving response content.
        for j, response in enumerate(input_root.findall('response'), start=1):
            # Strip leading and trailing whitespace from response text.
            if response.text:
                response.text = response.text.strip()

            # Set new ID for each response, p1 to p10 represent prompts, r1 to r 100 represent responses
            new_id = f'p{i}-r{j}'
            response.set('id', new_id)
            merged_root.append(response)

    # Paths for the merged XML files in the general and specific directories.
    general_output_path = os.path.join(output_dir_general, output_file)
    specific_output_path = os.path.join(output_dir_specific, output_file)

    # Write the merged XML content to files in both directories, with pretty printing.
    tree = etree.ElementTree(merged_root)
    tree.write(general_output_path, pretty_print=True, xml_declaration=True, encoding='utf-8')
    tree.write(specific_output_path, pretty_print=True, xml_declaration=True, encoding='utf-8')

    print(f'Successfully written merged files to: {general_output_path} and {specific_output_path}')

# Configuration for different language combinations of prompt and response.
configurations = [
    ('../data/raw_data/raw_response', 'response_en_en_', '../data/raw_data/response_list/merged', 'response_en_en.xml', 'en', 'en'),
    ('../data/raw_data/raw_response', 'response_zh_en_', '../data/raw_data/response_list/merged', 'response_zh_en.xml', 'zh', 'en'),
    ('../data/raw_data/raw_response', 'response_en_zh_', '../data/raw_data/response_list/merged', 'response_en_zh.xml', 'en', 'zh'),
    ('../data/raw_data/raw_response', 'response_zh_zh_', '../data/raw_data/response_list/merged', 'response_zh_zh.xml', 'zh', 'zh')
]

# Execute merging for all configurations.
for input_dir, file_prefix, output_dir, output_file, prompt_type, response_type in configurations:
    merge_xml_files(input_dir, file_prefix, output_dir, output_file, prompt_type, response_type)
