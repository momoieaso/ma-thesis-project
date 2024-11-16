"""
Script Name: 11_plural_noun_frequency_zh.py
Description:
    - Analyzes XML files containing POS tagging results to calculate the frequency of plural nouns in Chinese responses.
    - Uses POS tags to identify plural nouns, without distinguishing singular nouns.
    - Computes the average plural noun frequency, standard deviation, and coefficient of variation (CV) across all responses.
    - Outputs the statistics to a CSV file.
"""

import os
import csv
from lxml import etree
import numpy as np

input_dir = "../data/processed_data/pos/pos_tagging/merged/zh"
output_csv_path = "../data/processed_data/pos/plural_noun_frequency/plural_noun_frequency_zh.csv"

# Plural indicators based on word suffix and common plural words. 
suffix_plural = {"们"}
det_plural = {"各", "些"}
num_plural = {"诸", "许多"}

# POS tags for noun detection
noun_pos = {"NOUN"}
det_pos = {"DET"}
num_pos = {"NUM"}

def calculate_plural_noun_frequency_per_response(response):
    """Calculate the plural noun frequency for a single response using POS tags."""
    total_noun_count = 0
    plural_noun_count = 0

    # Iterate through all <t> elements in the response. 
    for token in response.findall(".//t"):
        word = token.text
        pos = token.get("pos")

        # Count all nouns and check for plural indicators. 
        if pos in noun_pos:
            total_noun_count += 1
            if any(suffix in word for suffix in suffix_plural):
                plural_noun_count += 1
        elif pos in det_pos and word in det_plural:
            plural_noun_count += 1
        elif pos in num_pos and word in num_plural:
            plural_noun_count += 1

    # Calculate plural noun frequency. 
    plural_frequency = plural_noun_count / total_noun_count if total_noun_count > 0 else 0

    return plural_frequency

def process_xml_file(file_path):
    """Process a single XML file and calculate average plural noun frequency, standard deviation, and CV."""
    tree = etree.parse(file_path)
    root = tree.getroot()

    response_frequencies = []

    # Iterate through each <response> element. 
    for response in root.findall(".//response"):
        plural_frequency = calculate_plural_noun_frequency_per_response(response)
        response_frequencies.append(plural_frequency)

    # Calculate statistics: mean, standard deviation, and coefficient of variation (CV). 
    average_frequency = np.mean(response_frequencies) if response_frequencies else 0
    std_dev = np.std(response_frequencies) if response_frequencies else 0
    cv = (std_dev / average_frequency * 100) if average_frequency > 0 else 0

    return len(response_frequencies), average_frequency, std_dev, cv

def process_all_files(input_dir, output_csv_path):
    """Process all XML files in the input folder and save the results to a CSV file."""
    # Ensure the output directory exists. 
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    # Prepare the output CSV file. 
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["File", "Total Responses", "Average Plural Frequency", "Standard Deviation", "CV"])

        # Iterate through all XML files in the input folder. 
        for file_name in os.listdir(input_dir):
            if file_name.endswith(".xml"):
                file_path = os.path.join(input_dir, file_name)
                total_responses, avg_frequency, std_dev, cv = process_xml_file(file_path)

                # Write statistics to the CSV file. 
                writer.writerow([file_name, total_responses, round(avg_frequency, 4), round(std_dev, 4), f"{cv:.2f}%"])
                print(f"Processed {file_name}: Avg Frequency={avg_frequency:.4f}, Std Dev={std_dev:.4f}, CV={cv:.2f}%")

    print(f"Results saved to {output_csv_path}")

if __name__ == "__main__":
    # Run the script. 
    process_all_files(input_dir, output_csv_path)
