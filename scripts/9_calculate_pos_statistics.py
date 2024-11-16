"""
Script Name: 9_calculate_pos_statistics.py
Description:
    - This script processes JSON files containing part-of-speech (POS) counts for responses, calculates the relative frequency of each POS tag, and aggregates statistics (mean, standard deviation, and coefficient of variation).
    - Supports two modes using configurations:
        1. Separate files mode: Analyzes 40 JSON files in a specified directory.
        2. Merged files mode: Analyzes 4 merged JSON files in a different directory.
    - Outputs the POS statistics JSON files to two specified output directories with filenames prefixed as "pos_frequency_".
"""

import json
import os
import numpy as np

# Define the order of POS tags for consistency in processing.
pos_order = ['NOUN', 'PROPN', 'VERB', 'AUX', 'ADJ', 'ADV', 'PRON', 'NUM', 'DET', 'PART', 'CCONJ', 'SCONJ', 'ADP', 'INTJ', 'PUNCT', 'X', 'NON-ZH']

def calculate_stats(input_dir, output_dir_general, output_dir_specific):
    """Calculate statistics (mean, std dev, and CV) for POS tags from input JSON files."""
    # Ensure both output directories exist.
    os.makedirs(output_dir_general, exist_ok=True)
    os.makedirs(output_dir_specific, exist_ok=True)

    # Get a sorted list of all JSON files in the input directory.
    input_files = sorted([file for file in os.listdir(input_dir) if file.endswith('.json')])

    for filename in input_files:
        all_stats = {}
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Calculate total counts and relative frequencies for each response.
        total_counts = [sum(response['pos_counts'].get(pos, 0) for pos in pos_order) for response in data]
        pos_relative_frequencies = {
            pos: [
                response['pos_counts'].get(pos, 0) / total if total > 0 else 0
                for response, total in zip(data, total_counts)
            ]
            for pos in pos_order
        }

        # Compute statistics for each POS tag.
        file_stats = {
            pos: {
                'mean': round(np.mean(frequencies), 4) if frequencies else 0,
                'std_dev': round(np.std(frequencies), 4) if frequencies else 0,
                'cv': round((np.std(frequencies) / np.mean(frequencies) * 100), 4) if frequencies and np.mean(frequencies) > 0 else 0
            }
            for pos, frequencies in pos_relative_frequencies.items()
        }
        all_stats[filename[:-5]] = file_stats

        # Define the output filename by replacing the prefix.
        output_filename = filename.replace('pos_tag_counting_', 'pos_frequency_')

        # Define output paths for both general and specific directories.
        output_file_path_general = os.path.join(output_dir_general, output_filename)
        output_file_path_specific = os.path.join(output_dir_specific, output_filename)

        # Save statistics to JSON files in both directories.
        with open(output_file_path_general, 'w', encoding='utf-8') as f:
            json.dump(all_stats, f, indent=4)
        with open(output_file_path_specific, 'w', encoding='utf-8') as f:
            json.dump(all_stats, f, indent=4)

        print(f"Statistics saved to:")
        print(f"  - {output_file_path_general}")
        print(f"  - {output_file_path_specific}")

# Configuration setup for separate and merged file processing.
configurations = [
    # Separate files mode.
    ('../data/processed_data/pos/pos_tag_counting/separate/en', '../data/processed_data/pos/pos_frequency/separate/all', '../data/processed_data/pos/pos_frequency/separate/en'),
    ('../data/processed_data/pos/pos_tag_counting/separate/zh', '../data/processed_data/pos/pos_frequency/separate/all', '../data/processed_data/pos/pos_frequency/separate/zh'),

    # Merged files mode.
    ('../data/processed_data/pos/pos_tag_counting/merged/en', '../data/processed_data/pos/pos_frequency/merged/all', '../data/processed_data/pos/pos_frequency/merged/en'),
    ('../data/processed_data/pos/pos_tag_counting/merged/zh', '../data/processed_data/pos/pos_frequency/merged/all', '../data/processed_data/pos/pos_frequency/merged/zh')
]

# Execute POS statistics calculation for all configurations.
for input_dir, output_dir_general, output_dir_specific in configurations:
    print(f"Starting POS statistics calculation for files in {input_dir}...")
    calculate_stats(input_dir, output_dir_general, output_dir_specific)
    print(f"All files in {input_dir} have been processed and saved to both directories.")
