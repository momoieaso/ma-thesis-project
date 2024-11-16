"""
Script Name: 4_extract_text_from_xml_responses.py
Description:
    - Extracts text content from <response> tags in XML files.
    - Saves the extracted text to separate plain text files.
    - Supports batch processing of multiple XML files in a specified input folder.
"""

import os
import xml.etree.ElementTree as ET

def extract_text_from_xml(input_xml_path, output_txt_path, tag_name="response", max_responses=1000):
    # Parse the XML file. 
    tree = ET.parse(input_xml_path)
    root = tree.getroot()
    
    # Open the output text file. 
    with open(output_txt_path, "w", encoding="utf-8") as f:
        # Find all specified tags in the XML file. 
        responses = root.findall(f".//{tag_name}")
        
        # Extract text content from each tag. 
        for i, response in enumerate(responses[:max_responses]):
            if response.text:  # Ensure the text is not empty. 
                f.write(response.text.strip() + "\n")  # Write cleaned text. 
            print(f"Processed response {i + 1} in {os.path.basename(input_xml_path)}")
            
    print(f"Extraction completed for {os.path.basename(input_xml_path)}. Results saved in {output_txt_path}")

def process_xml_files(input_dir, output_dir, tag_name="response", max_responses=1000):
    # Iterate through all XML files in the input directory. 
    for filename in os.listdir(input_dir):
        if filename.endswith(".xml"):
            xml_file = os.path.join(input_dir, filename)
            output_txt_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.txt")
            
            # Extract text from the current XML file. 
            extract_text_from_xml(xml_file, output_txt_path, tag_name, max_responses)

input_dir = "../data/raw_data/response_list/merged/all"  # Input directory containing XML files. 
output_dir = "../data/raw_data/response_text_merged"  # Output directory for text files. 

# Create the output directory if it does not exist. 
os.makedirs(output_dir, exist_ok=True)

# Process all XML files in the input directory. 
process_xml_files(input_dir, output_dir)
