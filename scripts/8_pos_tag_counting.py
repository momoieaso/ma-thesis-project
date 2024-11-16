"""
Script Name: 8_pos_tag_counting.py
Description:
    - Processes XML files containing linguistic annotations, calculates the frequency of part-of-speech (POS) tags for each response, and saves the statistics to JSON files.
    - Supports two modes:
        1. Separate files mode: Analyzes 40 XML files, each containing 100 responses.
        2. Merged files mode: Analyzes 4 XML files, each containing 1000 responses.
    - Outputs the POS statistics JSON files to two specified output directories for each mode, with the prefix "pos_tag_counting_" added to the file names.
"""

import lxml.etree as ET
from collections import Counter
import json
import os

def count_pos_tags(input_file, output_dir_general, output_dir_specific):
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    # Get the total number of responses to monitor progress. 
    total_responses = len(root.findall('.//response'))
    
    # Store POS frequency for each response. 
    pos_tags_counts_per_response = []
    
    # Iterate over each response to collect POS statistics. 
    for index, response in enumerate(root.findall('.//response')):
        pos_counter = Counter()
        tag_counter = Counter()
        
        # Iterate over each sentence to count POS tags.
        for sentence in response.findall('.//s'):
            tokens = sentence.findall('.//t')
            pos_counter.update([token.get('pos') for token in tokens if token.get('pos')])  # Exclude empty POS tags.
            tag_counter.update([token.get('tag') for token in tokens if token.get('tag')])  # Exclude empty tags.
        
        # Add each response's POS counts to the list.
        pos_tags_counts_per_response.append({
            "response_id": response.get('id'),
            "pos_counts": dict(pos_counter),
            "tag_counts": dict(tag_counter)
})
        
        # Print progress information.
        print(f"Processed response {index + 1}/{total_responses} in file {os.path.basename(input_file)}")

    # Construct JSON output filename with "pos_tag_counting_" prefix.
    output_filename = os.path.basename(input_file).replace('.xml', '.json').replace('pos_tagging_', 'pos_tag_counting_')

    # Define output paths for both general and specific directories.
    output_file_path_general = os.path.join(output_dir_general, output_filename)
    output_file_path_specific = os.path.join(output_dir_specific, output_filename)

    # Ensure both output directories exist.
    if not os.path.exists(output_dir_general):
        os.makedirs(output_dir_general)
    if not os.path.exists(output_dir_specific):
        os.makedirs(output_dir_specific)

    # Save the statistics to JSON files in both directories.
    with open(output_file_path_general, 'w', encoding='utf-8') as output_file:
        json.dump(pos_tags_counts_per_response, output_file, ensure_ascii=False, indent=4)
    with open(output_file_path_specific, 'w', encoding='utf-8') as output_file:
        json.dump(pos_tags_counts_per_response, output_file, ensure_ascii=False, indent=4)

    # Print completion message.
    print(f"POS counts and tag counts saved to:")
    print(f"  - {output_file_path_general}")
    print(f"  - {output_file_path_specific}")

# Configuration setup for separate and merged file processing.
configurations = [
    # Separate files mode (40 files).
    ('../data/processed_data/pos/pos_tagging/separate/en', '../data/processed_data/pos/pos_tag_counting/separate/all', '../data/processed_data/pos/pos_tag_counting/separate/en'),
    ('../data/processed_data/pos/pos_tagging/separate/zh', '../data/processed_data/pos/pos_tag_counting/separate/all', '../data/processed_data/pos/pos_tag_counting/separate/zh'),

    # Merged files mode (4 files).
    ('../data/processed_data/pos/pos_tagging/merged/en', '../data/processed_data/pos/pos_tag_counting/merged/all', '../data/processed_data/pos/pos_tag_counting/merged/en'),
    ('../data/processed_data/pos/pos_tagging/merged/zh', '../data/processed_data/pos/pos_tag_counting/merged/all', '../data/processed_data/pos/pos_tag_counting/merged/zh')
]

# Execute POS tag counting for all configurations.
for input_dir, output_dir_general, output_dir_specific in configurations:
    print(f"Starting POS tag counting for files in {input_dir}...")
    for input_file in os.listdir(input_dir):
        if input_file.endswith('.xml'):
            input_file_path = os.path.join(input_dir, input_file)
            count_pos_tags(input_file_path, output_dir_general, output_dir_specific)
    print(f"All files in {input_dir} have been processed and saved to both directories.")