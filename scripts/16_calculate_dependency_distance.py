"""
Script Name: 16_calculate_dependency_distance.py
Description:
    - Calculate the average dependency distance and its standard deviation as well as its coefficient of variation (CV) for 40 XML files with 100 responses in each.
    - The statistical results are saved into a CSV file and a JSON file. 
"""

import os
import numpy as np
from lxml import etree
import csv
import json
import re

def calculate_distance(responses):
    response_avg_distances = []

    for response in responses:
        total_distance = 0
        token_count = 0

        sentences = response.findall('s')
        for s_elem in sentences:
            tokens = s_elem.findall('t')
            for token in tokens:
                dep_distance = int(token.get('dep_distance'))
                total_distance += dep_distance
                token_count += 1 # The count of tokens. 

        avg_distance = total_distance / token_count if token_count > 0 else 0
        response_avg_distances.append(avg_distance)

    # Calculate the overall average dependency distance. 
    overall_avg_distance = np.mean(response_avg_distances) if response_avg_distances else 0

    # Calculate standard deviation. 
    std_dev = np.std(response_avg_distances) if response_avg_distances else 0

    # Calculate coefficient of variation (CV). 
    cv = (std_dev / overall_avg_distance * 100) if overall_avg_distance != 0 else 0

    return round(overall_avg_distance, 4), round(std_dev, 4), round(cv, 2), response_avg_distances


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
    # Ensure the output directory exists. 
    os.makedirs(os.path.dirname(output_file_csv), exist_ok=True)
    os.makedirs(os.path.dirname(output_file_json), exist_ok=True)

    results = []  # Store all results. 

    xml_files = [f for f in os.listdir(input_dir) if f.endswith(".xml")]
    sorted_files = sort_files(xml_files)

    # Create CSV file and write header row. 
    with open(output_file_csv, mode='w', newline='', encoding='utf-8') as file_csv:
        writer = csv.writer(file_csv)
        writer.writerow(["File Name", "Average Dependency Distance", "Standard Deviation", "Coefficient of Variation (CV)"])

        # Iterate over all XML files in the input folder. 
        for file_name in sorted_files:
            if file_name.endswith(".xml"):
                file_path = os.path.join(input_dir, file_name)

                # Parse XML file. 
                responses = etree.parse(file_path).getroot().findall('response')

                # Calculate dependency distances and CV. 
                overall_avg_distance, std_dev, cv, _ = calculate_distance(responses)

                # Write results to CSV, preserving three decimal places. 
                writer.writerow([file_name, f"{overall_avg_distance:.4f}", f"{std_dev:.4f}", f"{cv:.2f}%"])

                # Append results to the results list. 
                results.append({
                    "file_name": file_name,
                    "avg_distance": round(overall_avg_distance, 4),
                    "std_dev": round(std_dev, 4),
                    "cv": f"{round(cv, 2)}%"
                })

                print(f"Processed {file_name}.")

    # Save all results to a JSON file. 
    with open(output_file_json, 'w', encoding='utf-8') as file_json:
        json.dump(results, file_json, ensure_ascii=False, indent=4)

# Configuration setup for input and output directories and file names.
configurations = [
    # Configuration 1
    (
        '../data/processed_data/dependency/dependency_parsing/separate/all', 
        '../data/processed_data/dependency/dependency_distance/separate/dependency_distance_separate.csv', 
        '../data/processed_data/dependency/dependency_distance/separate/dependency_distance_separate.json'
    ),
    # Configuration 2
    (
        '../data/processed_data/dependency/dependency_parsing/merged/all', 
        '../data/processed_data/dependency/dependency_distance/merged/dependency_distance_merged.csv', 
        '../data/processed_data/dependency/dependency_distance/merged/dependency_distance_merged.json'
    )
]

# Execute processing for all configurations.
for input_dir, output_file_csv, output_file_json in configurations:
    print(f"Starting dependency distance calculation for files in {input_dir}...")
    process_xml_files(input_dir, output_file_csv, output_file_json)
    print(f"All files in {input_dir} have been processed and results saved to {output_file_csv} and {output_file_json}.")
