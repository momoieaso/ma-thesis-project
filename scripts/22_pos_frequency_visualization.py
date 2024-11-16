"""
Script Name: 22_pos_frequency_visualization.py
Description:
    - This script processes JSON files containing POS tag statistics and generates visualizations, including stacked bar charts, individual bar charts for each POS tag, and box plots for relative frequency distributions. 
    - The script supports two modes of operation:
        1. Separate file mode: Processes 40 individual files in the specified directories.
        2. Merged file mode: Processes 4 merged files in different directories.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np
import re

# Define the order of POS tags and their color mapping. 
pos_order = ['NOUN', 'PROPN', 'VERB', 'AUX', 'ADJ', 'ADV', 'PRON', 'NUM', 'DET', 
             'PART', 'CCONJ', 'SCONJ', 'ADP', 'INTJ', 'PUNCT', 'X', 'NON-ZH']
color_palette = plt.get_cmap('tab20', len(pos_order))  # Define color palette. 
pos_colors = {pos: color_palette(i) for i, pos in enumerate(pos_order)}  # Map each POS to a color. 

# Define legend elements for POS tags. 
legend_elements = [plt.Line2D([0], [0], color=pos_colors[pos], lw=4, label=pos) for pos in pos_order]

# Configuration list for input and output directories. 
configurations = [
    {
        "frequency_input_dir": '../data/processed_data/pos/pos_frequency/separate/all',
        "counting_input_dir": '../data/processed_data/pos/pos_tag_counting/separate/all',
        "output_dir": '../visualization/pos_frequency/separate',
        "is_merged": False
    },
    {
        "frequency_input_dir": '../data/processed_data/pos/pos_frequency/merged/all',
        "counting_input_dir": '../data/processed_data/pos/pos_tag_counting/merged/all',
        "output_dir": '../visualization/pos_frequency/merged',
        "is_merged": True
    }
]

# Custom sorting function to order files by language pairs and file numbers. 
def custom_sort(file_name, is_merged=False):
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

# Read POS frequency data from JSON files. 
def read_frequency_data(input_dir, is_merged):
    """Read POS frequency data from JSON files."""
    pos_data = {pos: [] for pos in pos_order}  # Initialize data structure for each POS. 
    input_files = sorted([file for file in os.listdir(input_dir) if file.endswith('.json')],
                         key=lambda x: custom_sort(x, is_merged))

    file_names = []

    for filename in input_files:
        file_path = os.path.join(input_dir, filename)
        file_names.append(os.path.splitext(filename)[0])
        with open(file_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)
            top_level_key = list(stats.keys())[0]  # Retrieve main key name. 
            # Append mean values for each POS tag. 
            for pos in pos_order:
                pos_data[pos].append(stats[top_level_key].get(pos, {}).get('mean', 0))

    return pos_data, file_names

# Read POS counting data for box plot visualization. 
def read_counting_data(input_dir, is_merged):
    """Read POS counting data from JSON files."""
    pos_data = {pos: [] for pos in pos_order}  # Initialize data structure for each POS. 
    input_files = sorted([file for file in os.listdir(input_dir) if file.endswith('.json')],
                         key=lambda x: custom_sort(x, is_merged))

    file_names = []

    for filename in input_files:
        file_path = os.path.join(input_dir, filename)
        file_names.append(os.path.splitext(filename)[0])
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for pos in pos_order:
                # Calculate relative frequencies for each response in a file. 
                pos_frequencies = [
                    response['pos_counts'].get(pos, 0) / sum(response['pos_counts'].values())
                    if sum(response['pos_counts'].values()) > 0 else 0
                    for response in data
                ]
                pos_data[pos].append(pos_frequencies)

    return pos_data, file_names

# Plot stacked bar chart for POS tag distribution per file. 
def plot_stacked_bar_chart(pos_data, file_names, output_dir, is_merged):
    """Plot stacked bar chart for POS tag distribution per file."""
    full_output_dir = os.path.join(output_dir, 'bar chart')
    os.makedirs(full_output_dir, exist_ok=True) 
    
    fig, ax = plt.subplots(figsize=(15, 8))
    bottom = np.zeros(len(file_names))  # Initialize bottom for stacking. 

    # Create stacked bars for each POS tag. 
    for pos in pos_order:
        ax.bar(file_names, pos_data[pos], bottom=bottom, color=pos_colors[pos], label=pos)
        bottom += np.array(pos_data[pos])

    # Add vertical dashed lines for grouping. 
    for i in range(4, len(file_names), 4):
        plt.axvline(x=i - 0.5, color='gray', linestyle='--', linewidth=1)

    ax.set_xlabel('File Names')
    ax.set_ylabel('Relative Frequency')
    ax.set_title('POS Tag Distribution per File (Stacked Bar Chart)')
    ax.legend(handles=legend_elements, title='POS Tags', loc='upper left', bbox_to_anchor=(1, 1))
    plt.xlim(-0.6, len(file_names) - 0.4)
    plt.xticks(rotation=0 if is_merged else 90)
    plt.tight_layout()
    plt.savefig(os.path.join(full_output_dir, 'stacked_bar_chart_pos_distribution.png'))
    plt.close()

# Plot individual bar chart for each POS tag. 
def plot_bar_chart_per_pos(pos_data, file_names, output_dir, is_merged):
    """Plot bar charts for each POS tag."""
    full_output_dir = os.path.join(output_dir, 'bar chart')
    os.makedirs(full_output_dir, exist_ok=True)  
    
    for pos in pos_order:
        plt.figure(figsize=(15, 8))
        plt.bar(file_names, pos_data[pos], color=pos_colors[pos])

        # Add vertical dashed lines for grouping. 
        for i in range(4, len(file_names), 4):
            plt.axvline(x=i - 0.5, color='gray', linestyle='--', linewidth=1)

        plt.xlabel('File Names')
        plt.ylabel('Relative Frequency')
        plt.title(f'Relative Frequency of {pos} per File')
        plt.xlim(-0.6, len(file_names) - 0.4)
        plt.xticks(rotation=0 if is_merged else 90)
        plt.tight_layout()
        plt.savefig(os.path.join(full_output_dir, f'bar_chart_{pos}_frequency.png'))
        plt.close()

# Plot box plot for each POS tag across all files. 
def plot_box_plot_per_pos(pos_data, file_names, output_dir, is_merged):
    """Plot box plot for each POS tag across all files."""
    full_output_dir = os.path.join(output_dir, 'box plot')
    os.makedirs(full_output_dir, exist_ok=True)  
    
    for pos in pos_order:
        box_data = pos_data[pos]
        data_dict = {file_name: data for file_name, data in zip(file_names, box_data)}
        sorted_box_data = [data_dict[name] for name in file_names]

        plt.figure(figsize=(15, 8))
        box_plot = plt.boxplot(sorted_box_data, tick_labels=file_names, patch_artist=True)
        
        # Set color for each box. 
        for patch in box_plot['boxes']:
            patch.set_facecolor(pos_colors[pos])
        
        # Add vertical dashed lines for grouping. 
        positions = [median.get_xdata()[0] for median in box_plot['medians']]
        for i in range(4, len(positions), 4):
            plt.axvline(x=positions[i] - 0.25, color='gray', linestyle='--', linewidth=1)

        plt.xlabel('File Names')
        plt.ylabel('Relative Frequency')
        plt.title(f'Box Plot of Relative Frequency of {pos}')
        plt.xticks(rotation=0 if is_merged else 90)
        plt.tight_layout()
        plt.savefig(os.path.join(full_output_dir, f'box_plot_{pos}_relative_frequency.png'))
        plt.close()

# Main function to process each configuration. 
def main():
    for config in configurations:
        frequency_input_dir = config["frequency_input_dir"]
        counting_input_dir = config["counting_input_dir"]
        output_dir = config["output_dir"]
        is_merged = config["is_merged"]
        os.makedirs(output_dir, exist_ok=True)

        print(f"Reading POS frequency data from {frequency_input_dir}...")
        frequency_data, file_names = read_frequency_data(frequency_input_dir, is_merged)

        print(f"Reading POS counting data from {counting_input_dir}...")
        counting_data, _ = read_counting_data(counting_input_dir, is_merged)

        print(f"Generating stacked bar chart for {output_dir}...")
        plot_stacked_bar_chart(frequency_data, file_names, output_dir, is_merged)

        print(f"Generating bar charts for each POS tag for {output_dir}...")
        plot_bar_chart_per_pos(frequency_data, file_names, output_dir, is_merged)

        print(f"Generating box plots for POS tag relative frequencies for {output_dir}...")
        plot_box_plot_per_pos(counting_data, file_names, output_dir, is_merged)

        print(f"All figures saved to {output_dir}.")

if __name__ == "__main__":
    main()
    print("All configurations have been processed and visualizations generated.")
