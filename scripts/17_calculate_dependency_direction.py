"""
Script Name: 17_calculate_dependency_direction.py
Description:
    - Calculates the proportions of dependencies where the dependent is before or after the head for 40 XML files with 100 responses in each. 
    - The statistics include average proportion of the dependency direction and its standard deviation as well as its coefficient of variation (CV). 
    - The statistical results are saved into a CSV file and a JSON file. 
"""

import os
import csv
import numpy as np
import json
from lxml import etree
import re

def calculate_dependency_proportions(responses):
    proportions = []
    for response in responses:
        before_count = 0
        after_count = 0
        sentences = response.findall('s')
        for s_elem in sentences:
            token_to_id = {token.text: int(token.get('id').split('-t')[-1]) for token in s_elem.findall('t')}  
            tokens = s_elem.findall('t')
            for token in tokens:
                token_id = int(token.get('id').split('-t')[-1])
                head_text = token.get('head')
                head_id = token_to_id.get(head_text)
                
                if head_id and head_id > token_id:
                    before_count += 1
                elif head_id and head_id < token_id:
                    after_count += 1
        
        total_count = before_count + after_count
        if total_count > 0:
            before_proportion = before_count / total_count
            after_proportion = after_count / total_count
        else:
            before_proportion = after_proportion = 0
        proportions.append((before_proportion, after_proportion))
    
    return proportions


def extract_key(file_name):
    """Extracts the language pair and number from the file name, using them as sort keys."""
    pattern = r"(en_en|zh_en|en_zh|zh_zh)_(\d+)"
    match = re.search(pattern, file_name)
    if match:
        lang_group = match.group(1)
        num = int(match.group(2))  # Convert the extracted string number to an integer for proper numerical sorting. 
        return (lang_group, num)
    return ("", 0)


def sort_files(file_list):
    """Sort files in the order: en_en_1 to en_en_10, zh_en_1 to zh_en_10, en_zh_1 to en_zh_10, zh_zh_1 to zh_zh_10"""
    return sorted(file_list, key=extract_key)


def process_xml_files(input_dir, output_file_csv, output_file_json):
    os.makedirs(os.path.dirname(output_file_csv), exist_ok=True)
    results = []

    xml_files = [f for f in os.listdir(input_dir) if f.endswith(".xml")]
    sorted_files = sort_files(xml_files)

    with open(output_file_csv, mode='w', newline='', encoding='utf-8') as file_csv:
        writer = csv.writer(file_csv)
        writer.writerow(["File Name", "Average Before Proportion", "Std Dev Before", "CV Before", "Average After Proportion", "Std Dev After", "CV After"])

        for file_name in sorted_files:
            if file_name.endswith(".xml"):
                file_path = os.path.join(input_dir, file_name)
                responses = etree.parse(file_path).getroot().findall('response')
                proportions = calculate_dependency_proportions(responses)
                
                before_proportions = [p[0] for p in proportions]
                after_proportions = [p[1] for p in proportions]
                
                avg_before = np.mean(before_proportions)
                std_dev_before = np.std(before_proportions)
                cv_before = (std_dev_before / avg_before * 100) if avg_before > 0 else 0
                avg_after = np.mean(after_proportions)
                std_dev_after = np.std(after_proportions)
                cv_after = (std_dev_after / avg_after * 100) if avg_after > 0 else 0

                writer.writerow([file_name, f"{avg_before:.4f}", f"{std_dev_before:.4f}", f"{cv_before:.2f}%", f"{avg_after:.4f}", f"{std_dev_after:.4f}", f"{cv_after:.2f}%"])
                results.append({
                    "file_name": file_name,
                    "avg_before_proportion": round(avg_before, 4),
                    "std_dev_before": round(std_dev_before, 4),
                    "cv_before": f"{round(cv_before, 2)}%",
                    "avg_after_proportion": round(avg_after, 4),
                    "std_dev_after": round(std_dev_after, 4),
                    "cv_after": f"{round(cv_after, 2)}%"
                })

    with open(output_file_json, 'w', encoding='utf-8') as file_json:
        json.dump(results, file_json, ensure_ascii=False, indent=4)

# Configuration setup for input and output directories and file names.
configurations = [
    # Configuration 1
    (
        '../data/processed_data/dependency/dependency_parsing/separate/all', 
        '../data/processed_data/dependency/dependency_direction/separate/dependency_direction_separate.csv', 
        '../data/processed_data/dependency/dependency_direction/separate/dependency_direction_separate.json'
    ),
    # Configuration 2
    (
        '../data/processed_data/dependency/dependency_parsing/merged/all', 
        '../data/processed_data/dependency/dependency_direction/merged/dependency_direction_merged.csv', 
        '../data/processed_data/dependency/dependency_direction/merged/dependency_direction_merged.json'
    )
]

# Execute processing for all configurations.
for input_dir, output_file_csv, output_file_json in configurations:
    print(f"Starting dependency direction calculation for files in {input_dir}...")
    process_xml_files(input_dir, output_file_csv, output_file_json)
    print(f"All files in {input_dir} have been processed and results saved to {output_file_csv} and {output_file_json}.")
