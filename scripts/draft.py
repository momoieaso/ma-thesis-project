import os
import json
import matplotlib.pyplot as plt
import numpy as np
import re
import logging
import traceback

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 定义 POS 标签的顺序和颜色映射
pos_order = ['NOUN', 'PROPN', 'VERB', 'AUX', 'ADJ', 'ADV', 'PRON', 'NUM', 'DET',
             'PART', 'CCONJ', 'SCONJ', 'ADP', 'INTJ', 'PUNCT', 'X', 'NON-ZH']
color_palette = plt.get_cmap('tab20', len(pos_order))
pos_colors = {pos: color_palette(i) for i, pos in enumerate(pos_order)}

# 定义图例元素
legend_elements = [plt.Line2D([0], [0], color=pos_colors[pos], lw=4, label=pos) for pos in pos_order]

# 配置列表
configurations = [
    {
        "frequency_input_dir": '../data/processed_data/pos/pos_frequency/separate/all',
        "counting_input_dir": '../data/processed_data/pos/pos_tag_counting/separate/all',
        "output_dir": '../visualization/pos_frequency/separate',
        "is_merged": False,
        "frequency_file_prefix": 'pos_frequency_response_',
        "counting_file_prefix": 'pos_tag_counting_response_'
    },
    {
        "frequency_input_dir": '../data/processed_data/pos/pos_frequency/merged/all',
        "counting_input_dir": '../data/processed_data/pos/pos_tag_counting/merged/all',
        "output_dir": '../visualization/pos_frequency/merged',
        "is_merged": True,
        "frequency_file_prefix": 'pos_frequency_response_',
        "counting_file_prefix": 'pos_tag_counting_response_'
    }
]

# 自定义排序函数
def custom_sort(file_name, is_merged=False, file_prefix=''):
    if is_merged:
        pattern = rf"{file_prefix}(en|zh)_(en|zh)\.json"
        match = re.match(pattern, file_name)
        if match:
            lang1, lang2 = match.groups()
            order = {('en', 'en'): 0, ('zh', 'en'): 1, ('en', 'zh'): 2, ('zh', 'zh'): 3}
            return order.get((lang1, lang2), 999)
    else:
        pattern = rf"{file_prefix}(en|zh)_(en|zh)_(\d+)\.json"
        match = re.match(pattern, file_name)
        if match:
            lang1, lang2, num = match.groups()
            num = int(num)
            order = {('en', 'en'): 0, ('zh', 'en'): 1, ('en', 'zh'): 2, ('zh', 'zh'): 3}
            return (order.get((lang1, lang2), 999), num)
    logging.warning(f"Filename '{file_name}' does not match expected pattern.")
    return (999, 999)

# 读取 POS 频率数据
def read_frequency_data(input_dir, is_merged, file_prefix):
    """读取 POS 频率数据的函数。"""
    pos_data = {pos: [] for pos in pos_order}
    try:
        input_files = sorted([file for file in os.listdir(input_dir) if file.endswith('.json') and file.startswith(file_prefix)],
                             key=lambda x: custom_sort(x, is_merged, file_prefix))
    except FileNotFoundError as e:
        logging.error(f"Input directory not found: {input_dir}")
        return pos_data, []
    except Exception as e:
        logging.error(f"Error accessing input directory: {e}")
        traceback.print_exc()
        return pos_data, []

    file_names = []

    for filename in input_files:
        file_path = os.path.join(input_dir, filename)
        file_names.append(os.path.splitext(filename)[0])
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                if not stats:
                    logging.warning(f"No data found in file: {file_path}")
                    continue
                top_level_key = list(stats.keys())[0]
                for pos in pos_order:
                    pos_value = stats.get(top_level_key, {}).get(pos, {}).get('mean', 0)
                    pos_data[pos].append(pos_value)
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            traceback.print_exc()

    return pos_data, file_names

# 读取 POS 计数数据
def read_counting_data(input_dir, is_merged, file_prefix):
    """读取 POS 计数数据的函数。"""
    pos_data = {pos: [] for pos in pos_order}
    try:
        input_files = sorted([file for file in os.listdir(input_dir) if file.endswith('.json') and file.startswith(file_prefix)],
                             key=lambda x: custom_sort(x, is_merged, file_prefix))
    except FileNotFoundError as e:
        logging.error(f"Input directory not found: {input_dir}")
        return pos_data, []
    except Exception as e:
        logging.error(f"Error accessing input directory: {e}")
        traceback.print_exc()
        return pos_data, []

    file_names = []

    for filename in input_files:
        file_path = os.path.join(input_dir, filename)
        file_names.append(os.path.splitext(filename)[0])
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not data:
                    logging.warning(f"No data found in file: {file_path}")
                    continue
                for pos in pos_order:
                    pos_frequencies = []
                    for response in data:
                        pos_counts = response.get('pos_counts', {})
                        total_counts = sum(pos_counts.values())
                        if total_counts > 0:
                            frequency = pos_counts.get(pos, 0) / total_counts
                        else:
                            frequency = 0
                        pos_frequencies.append(frequency)
                    pos_data[pos].append(pos_frequencies)
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            traceback.print_exc()

    return pos_data, file_names

# 提取文件名的函数
def extract_file_name(name, is_merged, file_prefix):
    if is_merged:
        pattern = rf"{file_prefix}(en_en|zh_en|en_zh|zh_zh)"
    else:
        pattern = rf"{file_prefix}(en_en|zh_en|en_zh|zh_zh)_(\d+)"
    match = re.search(pattern, name)
    if match:
        return match.group(1)
    else:
        logging.warning(f"Filename '{name}' does not match expected pattern.")
        return name

# 绘制堆叠条形图
def plot_stacked_bar_chart(pos_data, file_names, output_dir, is_merged, file_prefix):
    """绘制堆叠条形图。"""
    try:
        file_names = [extract_file_name(name, is_merged, file_prefix) for name in file_names]
        full_output_dir = os.path.join(output_dir, 'bar chart')
        os.makedirs(full_output_dir, exist_ok=True)

        fig, ax = plt.subplots(figsize=(15, 8))
        bottom = np.zeros(len(file_names))

        for pos in pos_order:
            if pos in pos_data:
                ax.bar(file_names, pos_data[pos], bottom=bottom, color=pos_colors[pos], label=pos)
                bottom += np.array(pos_data[pos])
            else:
                logging.warning(f"POS tag '{pos}' not found in data.")

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
    except Exception as e:
        logging.error(f"Error generating stacked bar chart: {e}")
        traceback.print_exc()

# 绘制每个 POS 标签的条形图
def plot_bar_chart_per_pos(pos_data, file_names, output_dir, is_merged, file_prefix):
    """为每个 POS 标签绘制条形图。"""
    try:
        file_names = [extract_file_name(name, is_merged, file_prefix) for name in file_names]
        full_output_dir = os.path.join(output_dir, 'bar chart')
        os.makedirs(full_output_dir, exist_ok=True)

        for pos in pos_order:
            if pos in pos_data:
                plt.figure(figsize=(15, 8))
                plt.bar(file_names, pos_data[pos], color=pos_colors[pos])

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
            else:
                logging.warning(f"POS tag '{pos}' not found in data.")
    except Exception as e:
        logging.error(f"Error generating bar charts for POS tags: {e}")
        traceback.print_exc()

# 绘制每个 POS 标签的箱线图
def plot_box_plot_per_pos(pos_data, file_names, output_dir, is_merged, file_prefix):
    """为每个 POS 标签绘制箱线图。"""
    try:
        file_names = [extract_file_name(name, is_merged, file_prefix) for name in file_names]
        full_output_dir = os.path.join(output_dir, 'box plot')
        os.makedirs(full_output_dir, exist_ok=True)

        for pos in pos_order:
            if pos in pos_data:
                box_data = pos_data[pos]
                data_dict = {file_name: data for file_name, data in zip(file_names, box_data)}
                sorted_box_data = [data_dict[name] for name in file_names if name in data_dict]

                plt.figure(figsize=(15, 8))
                box_plot = plt.boxplot(sorted_box_data, tick_labels=file_names, patch_artist=True)

                for patch in box_plot['boxes']:
                    patch.set_facecolor(pos_colors[pos])

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
            else:
                logging.warning(f"POS tag '{pos}' not found in data.")
    except Exception as e:
        logging.error(f"Error generating box plots for POS tags: {e}")
        traceback.print_exc()

# 主函数
def main():
    try:
        for config in configurations:
            frequency_input_dir = config["frequency_input_dir"]
            counting_input_dir = config["counting_input_dir"]
            output_dir = config["output_dir"]
            is_merged = config["is_merged"]
            frequency_file_prefix = config["frequency_file_prefix"]
            counting_file_prefix = config["counting_file_prefix"]
            os.makedirs(output_dir, exist_ok=True)

            logging.info(f"Reading POS frequency data from {frequency_input_dir}...")
            frequency_data, file_names = read_frequency_data(frequency_input_dir, is_merged, frequency_file_prefix)

            if not file_names:
                logging.warning(f"No files found in directory: {frequency_input_dir}")
                continue

            logging.info(f"Reading POS counting data from {counting_input_dir}...")
            counting_data, _ = read_counting_data(counting_input_dir, is_merged, counting_file_prefix)

            logging.info(f"Generating stacked bar chart for {output_dir}...")
            plot_stacked_bar_chart(frequency_data, file_names, output_dir, is_merged, frequency_file_prefix)

            logging.info(f"Generating bar charts for each POS tag for {output_dir}...")
            plot_bar_chart_per_pos(frequency_data, file_names, output_dir, is_merged, frequency_file_prefix)

            logging.info(f"Generating box plots for POS tag relative frequencies for {output_dir}...")
            plot_box_plot_per_pos(counting_data, file_names, output_dir, is_merged, counting_file_prefix)

            logging.info(f"All figures saved to {output_dir}.")

        logging.info("All configurations have been processed and visualizations generated.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
    print("All configurations have been processed and visualizations generated.")
