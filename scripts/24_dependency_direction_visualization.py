"""
Script Name: 24_dependency_direction_visualization.py
Description:
    - This script reads dependency direction statistics from CSV files, sorts the data based on specified language pair order, and generates bar charts for 'before' and 'after' proportions.
    - It supports both 'separate' and 'merged' modes, and differentiates between language pairs ('en_en', 'zh_en', 'en_zh', 'zh_zh') using distinct colors.

Outputs:
    - Bar charts for 'before' and 'after' average dependency proportions per file.
    - All generated figures are saved to the specified output directories.
"""

import os
import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import re

# Define color mapping for different language pairs. 
color_mapping = {
    'en_en': 'skyblue',
    'zh_en': 'lightgreen',
    'en_zh': 'lightcoral',
    'zh_zh': 'mediumpurple'
}

# Define legend elements for the plot. 
legend_elements = [
    Patch(facecolor='skyblue', label='en_en'),
    Patch(facecolor='lightgreen', label='zh_en'),
    Patch(facecolor='lightcoral', label='en_zh'),
    Patch(facecolor='mediumpurple', label='zh_zh')
]

def custom_sort(file_name, is_merged):
    """
    Custom sorting function:
    - For separate mode (is_merged=False): Sort in the order of en_en_1, zh_en_1, en_zh_1, zh_zh_1, en_en_2, zh_en_2, en_zh_2, zh_zh_2, etc.
    - For merged mode (is_merged=True): Sort by language pair order (en_en, zh_en, en_zh, zh_zh).
    """
    if is_merged:
        # Merged mode: Sort only by language pair order.
        pattern = r"(en_en|zh_en|en_zh|zh_zh)"
        match = re.search(pattern, file_name)
        if match:
            lang_group = match.group(1)
            order = {'en_en': 0, 'zh_en': 1, 'en_zh': 2, 'zh_zh': 3}
            return order.get(lang_group, 999)
        return 999
    else:
        # Separate mode: Sort by language pair and then by number.
        pattern = r"(en_en|zh_en|en_zh|zh_zh)_(\d+)"
        match = re.search(pattern, file_name)
        if match:
            lang_group = match.group(1)
            num = int(match.group(2))
            order = {'en_en': 0, 'zh_en': 1, 'en_zh': 2, 'zh_zh': 3}
            return (num, order.get(lang_group, 999))
        return (999, 999)  # Default high value for non-matching files.


def read_csv_data(file_path, is_merged):
    """
    Read CSV data and return a sorted list of tuples:
    (file_name, before_proportion, after_proportion).
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            file_name = row['File Name']
            before_proportion = float(row['Average Before Proportion'])
            after_proportion = float(row['Average After Proportion'])
            data.append((file_name, before_proportion, after_proportion))

    # Sort data using the custom sorting function. 
    data.sort(key=lambda x: custom_sort(x[0], is_merged))
    return data

def plot_bar_chart(data, output_dir, is_merged, chart_type):
    """
    Generate bar chart for 'before' or 'after' proportions.
    - data: List of tuples (file_name, before_proportion, after_proportion).
    - chart_type: 'before' or 'after' to specify the type of proportion to plot.
    """
    # Extract file names and remove prefixes for cleaner x-axis labels. 
    file_names = [re.search(r"(en_en|zh_en|en_zh|zh_zh)_(\d+)", name).group() if not is_merged else re.search(r"(en_en|zh_en|en_zh|zh_zh)", name).group() for name, _, _ in data]
    proportions = [item[1] if chart_type == 'before' else item[2] for item in data]
    colors = [color_mapping[re.search(r"(en_en|zh_en|en_zh|zh_zh)", name).group()] for name in file_names]

    plt.figure(figsize=(15, 8))
    plt.bar(file_names, proportions, color=colors)

    # Add vertical lines between different language pair . 
    for i in range(4, len(file_names), 4):
        plt.axvline(x=i - 0.5, color='gray', linestyle='--', linewidth=1)

    plt.xlim(-0.6, len(file_names) - 0.4)
    plt.legend(handles=legend_elements, title='Prompt Response', loc='upper left', bbox_to_anchor=(1, 1))
    plt.xlabel('File Names')
    plt.ylabel(f'Average {chart_type.capitalize()} Proportion')
    plt.title(f'Average {chart_type.capitalize()} Dependency Proportion per File')
    plt.xticks(rotation=0 if is_merged else 90)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'bar_chart_avg_{chart_type}_proportion.png'))
    plt.close()


def main():
    """Main function to process configurations and generate visualizations."""
    configurations = [
        {
            "csv_file": '../data/processed_data/dependency/dependency_direction/separate/dependency_direction_separate.csv',
            "output_dir": '../visualization/dependency_direction/separate',
            "is_merged": False
        },
        {
            "csv_file": '../data/processed_data/dependency/dependency_direction/merged/dependency_direction_merged.csv',
            "output_dir": '../visualization/dependency_direction/merged',
            "is_merged": True
        }
    ]

    for config in configurations:
        os.makedirs(config["output_dir"], exist_ok=True)

        print(f"Reading CSV data from {config['csv_file']}...")

        # Read and process CSV data. 
        csv_data = read_csv_data(config["csv_file"], config["is_merged"])

        # Generate bar charts for 'before' and 'after' proportions. 
        plot_bar_chart(csv_data, config["output_dir"], config["is_merged"], 'before')
        plot_bar_chart(csv_data, config["output_dir"], config["is_merged"], 'after')
        
        print(f"All figures saved to {config['output_dir']}.")

if __name__ == "__main__":
    main()
    print("All configurations have been processed and visualizations generated.")
