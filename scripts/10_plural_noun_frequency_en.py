"""
Script Name: 10_plural_noun_frequency_en.py
Description:
    - Analyzes XML files containing POS tagging results to calculate the frequency of plural nouns in English responses.
    - Computes the average plural noun frequency, standard deviation, and coefficient of variation (CV) across all responses.
    - Outputs the statistics to a CSV file with details for each XML file.
"""

import os
import csv
from lxml import etree
from collections import Counter
import numpy as np

input_dir = "../data/processed_data/pos/pos_tagging/merged/en"
output_csv_path = "../data/processed_data/pos/plural_noun_frequency/plural_noun_frequency_en.csv"

# Define noun tags for singular and plural. 
singular_tags = {"NN", "NNP"}
plural_tags = {"NNS", "NNPS"}

def calculate_plural_noun_frequency_per_response(response):
    """Calculate plural noun frequency for a single response."""
    noun_counter = Counter()

    # Iterate through all <t> elements in the response
    for token in response.findall(".//t"):
        tag = token.get("tag")
        if tag in singular_tags:
            noun_counter["singular"] += 1
        elif tag in plural_tags:
            noun_counter["plural"] += 1

    # Calculate total nouns and plural frequency for the response. 
    total_nouns = noun_counter["singular"] + noun_counter["plural"]
    plural_frequency = noun_counter["plural"] / total_nouns if total_nouns > 0 else 0

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

    # Calculate statistics. 
    average_frequency = np.mean(response_frequencies) if response_frequencies else 0
    std_dev = np.std(response_frequencies) if response_frequencies else 0
    cv = (std_dev / average_frequency * 100) if average_frequency > 0 else 0

    return len(response_frequencies), average_frequency, std_dev, cv

def process_all_files(input_dir, output_csv_path):
    """Process all XML files in the input folder and save the results to CSV."""
    # Ensure the output directory exists. 
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    # Prepare output CSV file. 
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["File", "Total Responses", "Average Plural Frequency", "Standard Deviation", "CV"])

        # Iterate through all XML files in the input folder. 
        for file_name in os.listdir(input_dir):
            if file_name.endswith(".xml"):
                file_path = os.path.join(input_dir, file_name)
                total_responses, avg_frequency, std_dev, cv = process_xml_file(file_path)

                # Write statistics to CSV. 
                writer.writerow([file_name, total_responses, round(avg_frequency, 4), round(std_dev, 4), f"{cv:.2f}%"])
                print(f"Processed {file_name}: Avg Frequency={avg_frequency:.4f}, Std Dev={std_dev:.4f}, CV={cv:.2f}%")

    print(f"Results saved to {output_csv_path}")

if __name__ == "__main__":
    # Execute the script. 
    process_all_files(input_dir, output_csv_path)
