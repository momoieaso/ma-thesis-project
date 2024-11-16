"""
Script Name: 23_dependency_distance_visualization.py
Description:
    - This script reads dependency distance statistics from CSV files and XML files, computes and visualizes the average dependency distance for different language pairs ('en_en', 'zh_en', 'en_zh', 'zh_zh'). 
    - It generates bar plots and box plots to show the distribution of dependency distances per file.
Outputs:
    - Bar chart showing the average dependency distance per file.
    - Box plot showing the distribution of dependency distances per file.
    - Figures are saved to the specified output directories. 
"""

import os
import csv
import matplotlib.pyplot as plt
import re
from lxml import etree

# Define color mapping for different language pairs. 
color_mapping = {
    'en_en': 'skyblue',
    'zh_en': 'lightgreen',
    'en_zh': 'lightcoral',
    'zh_zh': 'mediumpurple'
}

# Define legend elements for language pairs. 
legend_elements = [
    plt.Line2D([0], [0], color='skyblue', lw=4, label='en_en'),
    plt.Line2D([0], [0], color='lightgreen', lw=4, label='zh_en'),
    plt.Line2D([0], [0], color='lightcoral', lw=4, label='en_zh'),
    plt.Line2D([0], [0], color='mediumpurple', lw=4, label='zh_zh')
]


def custom_sort(file_name, is_merged):
    """
    Sort files based on the following rules:
    - For separate mode (is_merged=False): Sort by language pair (en_en, zh_en, en_zh, zh_zh), then by number (1 to 10).
    - For merged mode (is_merged=True): Sort only by language pair (en_en, zh_en, en_zh, zh_zh).
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
    """Read dependency distance data from CSV and return sorted results."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data.append((row['File Name'], float(row['Average Dependency Distance'])))
    data.sort(key=lambda x: custom_sort(x[0], is_merged))
    return data

def read_xml_data(input_dir, is_merged):
    """Read XML files and calculate average dependency distance for each response."""
    xml_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.xml')], key=lambda x: custom_sort(x, is_merged))
    distances = []
    file_names = []

    for file_name in xml_files:
        file_path = os.path.join(input_dir, file_name)
        tree = etree.parse(file_path)
        responses = tree.getroot().findall('response')
        response_avg_distances = []

        # Calculate average dependency distance for each response. 
        for response in responses:
            total_distance = 0
            token_count = 0

            for s_elem in response.findall('s'):
                for token in s_elem.findall('t'):
                    dep_distance = int(token.get('dep_distance'))
                    total_distance += dep_distance
                    token_count += 1

            # Calculate average dependency distance for this response. 
            avg_distance = total_distance / token_count if token_count > 0 else 0
            response_avg_distances.append(avg_distance)

        # Store the average distances for all responses in this file. 
        distances.append(response_avg_distances)
        file_names.append(os.path.splitext(file_name)[0])

    return distances, file_names

def plot_bar_chart(data, output_dir, is_merged):
    """Create a bar chart for average dependency distances per file."""
    file_names = [re.search(r"(en_en|zh_en|en_zh|zh_zh)_(\d+)", name).group() if not is_merged else re.search(r"(en_en|zh_en|en_zh|zh_zh)", name).group() for name, _ in data]
    avg_distances = [item[1] for item in data]
    colors = [color_mapping[re.search(r"(en_en|zh_en|en_zh|zh_zh)", name).group()] for name in file_names]

    plt.figure(figsize=(15, 8))
    plt.bar(file_names, avg_distances, color=colors)

    for i in range(4, len(file_names), 4):
        plt.axvline(x=i - 0.5, color='gray', linestyle='--', linewidth=1)

    plt.xlim(-0.6, len(file_names) - 0.4)
    plt.legend(handles=legend_elements, title='Prompt Response', loc='upper left', bbox_to_anchor=(1, 1))

    plt.xlabel('File Names')
    plt.ylabel('Average Dependency Distance')
    plt.title('Average Dependency Distance per File')
    plt.xticks(rotation=0 if is_merged else 90)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'bar_chart_avg_dependency_distance.png'))
    plt.close()

def plot_box_plot(distances, file_names, output_dir, is_merged):
    """Create a box plot for dependency distance distribution per file."""
    file_names = [re.search(r"(en_en|zh_en|en_zh|zh_zh)_(\d+)", name).group() if not is_merged else re.search(r"(en_en|zh_en|en_zh|zh_zh)", name).group() for name in file_names]
    plt.figure(figsize=(15, 8))
    box_plot = plt.boxplot(distances, tick_labels=file_names, patch_artist=True)

    for patch, file_name in zip(box_plot['boxes'], file_names):
        lang_pair = re.search(r"(en_en|zh_en|en_zh|zh_zh)", file_name).group()
        patch.set_facecolor(color_mapping[lang_pair])

    positions = [median.get_xdata()[0] for median in box_plot['medians']]
    for i in range(4, len(positions), 4):
        plt.axvline(x=positions[i] - 0.25, color='gray', linestyle='--', linewidth=1)

    plt.legend(handles=legend_elements, title='Prompt Response', loc='upper left', bbox_to_anchor=(1, 1))

    plt.xlabel('File Names')
    plt.ylabel('Dependency Distance')
    plt.title('Box Plot of Dependency Distance per File')
    plt.xticks(rotation=0 if is_merged else 90)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'box_plot_dependency_distance.png'))
    plt.close()

def main():
    """Main function to process configurations and generate visualizations."""
    configurations = [
        {
            "csv_file": '../data/processed_data/dependency/dependency_distance/separate/dependency_distance_separate.csv',
            "xml_dir": '../data/processed_data/dependency/dependency_parsing/separate/all',
            "output_dir": '../visualization/dependency_distance/separate',
            "is_merged": False
        },
        {
            "csv_file": '../data/processed_data/dependency/dependency_distance/merged/dependency_distance_merged.csv',
            "xml_dir": '../data/processed_data/dependency/dependency_parsing/merged/all',
            "output_dir": '../visualization/dependency_distance/merged',
            "is_merged": True
        }
    ]

    for config in configurations:
        os.makedirs(config["output_dir"], exist_ok=True)

        # Plot bar chart from CSV data. 
        print(f"Reading CSV data from {config['csv_file']}...")
        csv_data = read_csv_data(config["csv_file"], config["is_merged"])
        plot_bar_chart(csv_data, config["output_dir"], config["is_merged"])

        # Plot box plot from XML data. 
        print(f"Reading XML data from {config['xml_dir']}...")
        distances, file_names = read_xml_data(config["xml_dir"], config["is_merged"])
        plot_box_plot(distances, file_names, config["output_dir"], config["is_merged"])

        print(f"All figures saved to {config['output_dir']}.")

if __name__ == "__main__":
    main()
    print("All configurations have been processed and visualizations generated.")
