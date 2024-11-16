"""
Script Name: 16_calculate_perplexity_loss_statistics.py
Description:
    - This script processes JSON files from two folders containing analysis results, calculates statistics (mean, standard deviation, and coefficient of variation) for 'perplexity' and 'loss'.
    - For each input folder, it outputs:
        1. A CSV file with statistical results for each JSON file.
        2. A JSON file containing aggregated results for each JSON file in the folder.
    - This allows easy analysis and comparison of model evaluation metrics across different responses.
"""

import os
import json
import csv
import numpy as np

def calculate_statistics(input_folder, output_csv, output_json):
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    os.makedirs(os.path.dirname(output_json), exist_ok=True)

    results = []

    # Iterate through each JSON file in the input folder.
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_file = os.path.join(input_folder, filename)

            # Load JSON data from the file.
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract the first 1000 records of 'perplexity' and 'loss'.
            perplexities = [entry["perplexity"] for entry in data[:1000]]
            losses = [entry["loss"] for entry in data[:1000]]
            count = min(len(data), 1000)

            # Calculate statistics for 'perplexity'.
            avg_perplexity = np.mean(perplexities) if count > 0 else 0
            std_dev_perplexity = np.std(perplexities) if count > 0 else 0
            cv_perplexity = (std_dev_perplexity / avg_perplexity * 100) if avg_perplexity > 0 else 0

            # Calculate statistics for 'loss'.
            avg_loss = np.mean(losses) if count > 0 else 0
            std_dev_loss = np.std(losses) if count > 0 else 0
            cv_loss = (std_dev_loss / avg_loss * 100) if avg_loss > 0 else 0

            # Append results for the current file.
            results.append({
                "input_folder": os.path.basename(input_folder),
                "file": filename,
                "average_perplexity": round(avg_perplexity, 4),
                "std_dev_perplexity": round(std_dev_perplexity, 4),
                "cv_perplexity": f"{round(cv_perplexity, 2)}%",
                "average_loss": round(avg_loss, 4),
                "std_dev_loss": round(std_dev_loss, 4),
                "cv_loss": f"{round(cv_loss, 2)}%"
            })

            print(f"Processed {filename}")

    # Save results to CSV file.
    with open(output_csv, "w", newline="", encoding="utf-8") as csv_file:
        fieldnames = [
            "input_folder", "file",
            "average_perplexity", "std_dev_perplexity", "cv_perplexity",
            "average_loss", "std_dev_loss", "cv_loss"
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Save results to JSON file.
    with open(output_json, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

    print(f"Results saved to {output_csv} and {output_json}")

# Configuration for input folders and output files.
configurations = [
    # Configuration 1
    (
        "../data/processed_data/perplexity/analysis_results/llama_results",  # Input folder 1
        "../data/processed_data/perplexity/calculation_statistics/llama_perplexity_loss_statistics.csv",  # Output CSV for folder 1
        "../data/processed_data/perplexity/calculation_statistics/llama_perplexity_loss_statistics.json"  # Output JSON for folder 1
    ),
    # Configuration 2
    (
        "../data/processed_data/perplexity/analysis_results/qwen_results",  # Input folder 2
        "../data/processed_data/perplexity/calculation_statistics/qwen_perplexity_loss_statistics.csv",  # Output CSV for folder 2
        "../data/processed_data/perplexity/calculation_statistics/qwen_perplexity_loss_statistics.json"  # Output JSON for folder 2
    )
]

# Execute the calculation for all configurations.
for input_folder, output_csv, output_json in configurations:
    print(f"Starting calculation for files in {input_folder}...")
    calculate_statistics(input_folder, output_csv, output_json)
    print(f"Completed processing for {input_folder}. Results saved to {output_csv} and {output_json}.")
