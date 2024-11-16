"""
Script Name: 21_text_statistics_visualization.py
Description:
    This script reads text statistics from JSON files, computes average token count and sentence count, and generates visualizations including bar plots and box plots for both 'separate' and 'merged' responses. The visualizations differentiate between prompt and response language pairs ('en_en', 'zh_en', 'en_zh', 'zh_zh') using distinct colors.

Outputs:
    - Bar plots for average token and sentence counts.
    - Box plots for token and sentence count distributions.
    - All generated figures are saved to the specified output directories.
"""

import os
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import re

# Configuration list for input and output directories. 
configurations = [
    {
        "input_dir": '../data/processed_data/text_statistics/separate/all',
        "output_dir": '../visualization/text_statistics/separate',
        "is_merged": False
    },
    {
        "input_dir": '../data/processed_data/text_statistics/merged/all',
        "output_dir": '../visualization/text_statistics/merged',
        "is_merged": True
    }
]

# Define color mapping for different language pairs. 
color_mapping = {
    'en_en': 'skyblue',
    'zh_en': 'lightgreen',
    'en_zh': 'lightcoral',
    'zh_zh': 'mediumpurple'
}

legend_elements = [
    Patch(facecolor='skyblue', label='en_en'),
    Patch(facecolor='lightgreen', label='zh_en'),
    Patch(facecolor='lightcoral', label='en_zh'),
    Patch(facecolor='mediumpurple', label='zh_zh')
]

# Custom sorting function for file names. 
def custom_sort(file_name, is_merged):
    if is_merged:
        match = re.search(r"(en_en|zh_en|en_zh|zh_zh)", file_name)
        if match:
            order = {'en_en': 0, 'zh_en': 1, 'en_zh': 2, 'zh_zh': 3}
            return order.get(match.group(1), 999)
    else:
        match = re.search(r"(en_en|zh_en|en_zh|zh_zh)_(\d+)", file_name)
        if match:
            lang_group = match.group(1)
            num = int(match.group(2))
            order = {'en_en': 0, 'zh_en': 1, 'en_zh': 2, 'zh_zh': 3}
            return (num, order.get(lang_group, 999))
    return (999, 999)

# Simplify file names for x-axis labels. 
def simplify_filename(file_name, is_merged):
    if is_merged:
        return re.search(r"(en_en|zh_en|en_zh|zh_zh)", file_name).group()
    else:
        match = re.search(r"(en_en|zh_en|en_zh|zh_zh)_(\d+)", file_name)
        return f"{match.group(1)}_{match.group(2)}" if match else ""
    
# Bar plot function. 
def plot_bar_chart(file_names, data, title, y_label, output_file, is_merged):
    plt.figure(figsize=(15, 8))
    colors = [color_mapping[re.search(r"(en_en|zh_en|en_zh|zh_zh)", name).group()] for name in file_names]
    plt.bar(file_names, data, color=colors)
    
    for i in range(4, len(file_names), 4):
        plt.axvline(x=i - 0.5, color='gray', linestyle='--', linewidth=1)

    plt.xlabel('File Names')
    plt.ylabel(y_label)
    plt.title(title)
    plt.xticks(rotation=0 if is_merged else 90)
    plt.xlim(-0.6, len(file_names) - 0.4)
    plt.legend(handles=legend_elements, title='Prompt Response', loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


# Box plot function. 
def plot_box_plot(file_names, data, title, y_label, output_file, is_merged):
    plt.figure(figsize=(15, 8))
    box_plot = plt.boxplot(data, labels=file_names, patch_artist=True)
    for patch, name in zip(box_plot['boxes'], file_names):
        patch.set_facecolor(color_mapping[re.search(r"(en_en|zh_en|en_zh|zh_zh)", name).group()])

    positions = [median.get_xdata()[0] for median in box_plot['medians']]
    for i in range(4, len(positions), 4):
        plt.axvline(x=positions[i] - 0.25, color='gray', linestyle='--', linewidth=1)

    plt.xlabel('File Names')
    plt.ylabel(y_label)
    plt.title(title)
    plt.xticks(rotation=0 if is_merged else 90)
    plt.legend(handles=legend_elements, title='Prompt Response', loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# Main function to process configurations. 
def main():
    for config in configurations:
        input_dir = config["input_dir"]
        output_dir = config["output_dir"]
        is_merged = config["is_merged"]

        os.makedirs(output_dir, exist_ok=True)

        # Get and sort JSON file list. 
        file_list = sorted(
            [file_name for file_name in os.listdir(input_dir) if file_name.endswith('.json')],
            key=lambda x: custom_sort(x, is_merged)
        )

        file_names = []
        avg_token_counts = []
        avg_sentence_counts = []
        token_counts_per_file = []
        sentence_counts_per_file = []

        # Read and process each JSON file. 
        for file_name in file_list:
            with open(os.path.join(input_dir, file_name), 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)

            file_names.append(simplify_filename(file_name, is_merged))
            token_counts = [item['token_count'] for item in data]
            sentence_counts = [item['sentence_count'] for item in data]

            avg_token_counts.append(np.mean(token_counts))
            avg_sentence_counts.append(np.mean(sentence_counts))
            token_counts_per_file.append(token_counts)
            sentence_counts_per_file.append(sentence_counts)

        # Plot bar charts. 
        plot_bar_chart(file_names, avg_token_counts, 'Average Token Count per Response File', 'Average Token Count', os.path.join(output_dir, 'bar_chart_average_token_count_per_response_file.png'), is_merged)
        plot_bar_chart(file_names, avg_sentence_counts, 'Average Sentence Count per Response File', 'Average Sentence Count', os.path.join(output_dir, 'bar_chart_average_sentence_count_per_response_file.png'), is_merged)

        # Plot box plots. 
        plot_box_plot(file_names, token_counts_per_file, 'Token Count Distribution per Response File', 'Token Count', os.path.join(output_dir, 'box_plot_average_token_count_per_response_file.png'), is_merged)
        plot_box_plot(file_names, sentence_counts_per_file, 'Sentence Count Distribution per Response File', 'Sentence Count', os.path.join(output_dir, 'box_plot_average_sentence_count_per_response_file.png'), is_merged)

        print(f"Processed and generated charts for: {output_dir}")

if __name__ == "__main__":
    main()
    print("All configurations have been processed and charts generated.")
