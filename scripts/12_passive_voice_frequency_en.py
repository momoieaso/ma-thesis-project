"""
Script Name: 12_passive_voice_frequency_en.py
Description:
    - Analyzes XML files containing POS tagging results to identify passive voice sentences in English responses.
    - For each response, calculates the frequency of passive voice sentences.
    - Computes the average passive voice frequency, standard deviation, and coefficient of variation (CV) across all responses.
    - Saves the results to a CSV file. 
    - For a sentence containing passive voice more than once, it is still counted as one, because we calculate the frequency based on the division of the number of sentences. 
"""

import os
import csv
from lxml import etree
import numpy as np

input_dir = "../data/processed_data/pos/pos_tagging/merged/en"
output_csv_path = "../data/processed_data/pos/passive_voice_frequency/passive_voice_frequency_en.csv"

# Ensure output directory exists. 
os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

def calculate_passive_frequency_per_response(response):
    """Calculate the passive voice sentence frequency for a single response."""
    passive_sentence_count = 0
    total_sentence_count = 0

    # Iterate through each sentence in the response. 
    for sentence in response.findall(".//s"):
        tokens = sentence.findall(".//t")
        is_passive = False

        # Check for AUX + VBN structure indicating passive voice. 
        for i in range(len(tokens) - 1):
            current_token = tokens[i]
            next_token = tokens[i + 1]

            if current_token.get("pos") == "AUX" and next_token.get("tag") == "VBN":
                is_passive = True
                break

        # Update counters. 
        total_sentence_count += 1
        if is_passive:
            passive_sentence_count += 1

    # Calculate passive sentence frequency for the response. 
    passive_frequency = passive_sentence_count / total_sentence_count if total_sentence_count > 0 else 0

    return passive_frequency


def process_xml_file(file_path):
    """Process a single XML file and calculate statistics for passive voice frequency."""
    tree = etree.parse(file_path)
    root = tree.getroot()

    response_frequencies = []

    # Iterate through each <response> element. 
    for response in root.findall(".//response"):
        passive_frequency = calculate_passive_frequency_per_response(response)
        response_frequencies.append(passive_frequency)
    
    # Calculate statistics. 
    average_frequency = np.mean(response_frequencies) if response_frequencies else 0
    std_dev = np.std(response_frequencies) if response_frequencies else 0
    cv = (std_dev / average_frequency * 100) if average_frequency > 0 else 0

    return len(response_frequencies), average_frequency, std_dev, cv


def process_all_files(input_dir, output_csv_path):
    """Process all XML files in the input folder and save the results to a CSV file."""
    # Ensure the output directory exists. 
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    # Prepare output CSV file. 
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["File Name", "Total Responses", "Average Passive Frequency", "Standard Deviation", "CV"])

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
    # Run the script. 
    process_all_files(input_dir, output_csv_path)
