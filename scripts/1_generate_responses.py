"""
Script Name: 1_generate_responses.py
Description:
    - Generate the responses with 40 prompts. The model used to generate the responses is GPT-4o-mini. The responses together with their prompts are stored in 40 XML files accordingly. The raw responses serve as a fundamental corpus to provide materials for further processing and analysis.
    - Four prompt files are divided according to the language of the prompt and the responses: English prompts to English responses, Chinese prompts to English responses, English prompts to Chinese responses and Chinese prompts to Chinese responses. In the experiment, the four types conresponds to en_en, zh_en, en_zh and zh_zh respectively. 
    - In each prompt file, there are 10 prompts. Prompts with the same sequence have the same meaning, regardless of the language of the prompt and the response. 
"""

import glob
from openai import OpenAI
import xml.etree.ElementTree as ET
import os

# Initialize the OpenAI client.
client = OpenAI()

# Define file paths.
script_path = os.path.dirname(__file__)  # The path to the current script.
prompt_path = os.path.join(script_path, '..', 'data', 'raw_data', 'prompt_list')  # The path to the prompt files.
response_path = os.path.join(script_path, '..', 'data', 'raw_data', 'raw_response')  # The path to the response files.

# Access the four prompt files.
prompt_files = glob.glob(os.path.join(prompt_path, 'prompt_*.txt'))
num_responses_per_prompt = 2  # Set the number of responses generated for each prompt.

for prompt_file_name in prompt_files:
    with open(prompt_file_name, 'r') as file:
        prompts = [line.strip() for line in file.readlines()]

    num_prompts = len(prompts)  # Get the sequence of the prompt.
    prompt_type = os.path.basename(prompt_file_name).replace('prompt_', '').replace('.txt', '')  # Get the combination of the source language and the target language.
    
    for i, prompt in enumerate(prompts, start=1):
        xml_response_content = f'<responses prompt_type="{prompt_type}">\n  <prompt_content>{prompt}</prompt_content>\n'

        # Generate the specified number (equals to num_responses_per_prompt) of responses for the current prompt.
        for j in range(1, num_responses_per_prompt + 1):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ]
            )
            response_content = response.choices[0].message.content
            xml_response_content += f'  <response id="{j}">\n    {response_content}\n  </response>\n'

        xml_response_content += '</responses>\n'
        
        # Construct the file name and path for storing the XML response.
        response_file_name = f'response_{prompt_type}_{i}.xml'  
        response_file_path = os.path.join(response_path, response_file_name)  
        
        # Write the response string to an XML file.
        with open(response_file_path, 'w') as response_xml_file:
            response_xml_file.write(xml_response_content)

        print(f"Processing {prompt_file_name} prompt {i}/{num_prompts}, completed {num_responses_per_prompt} responses.")

print("All responses have been processed and saved to their respective XML files in the 'raw_response' folder.")
