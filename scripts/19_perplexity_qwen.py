"""
Script Name: 19_perplexity_qwen.py

Description:
    - This script calculates the perplexity of response texts given a set of prompts using a pretrained language model, "Qwen/Qwen2.5-7B-Instruct".
    - It loads a model ("Qwen/Qwen2.5-7B-Instruct") and tokenizer from Hugging Face Hub, processes pairs of prompt and response files, and computes the perplexity for each response. The results are saved in JSON format, allowing for further analysis.
    - It loads prompts from text files and processes response files in batches of 100 lines, but masks the prompt part of the input and calculates loss only on the response part.

Requirements:
    - Ensure that the environment has access to GPU for faster computation, as the model and computations are resource-intensive.
    - The script requires the installation of the following Python packages:
        - `transformers`
        - `torch`
"""

import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer, TextGenerationPipeline
import torch

# Model name for loading from Hugging Face Hub. 
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

# Directory paths. 
prompt_dir = "../data/raw_data/prompt_list"
response_dir = "../data/raw_data/response_text_merged"
output_dir = "../data/processed_data/perplexity/analysis_results/qwen_results"


class PerplexityTextGenerationPipeline(TextGenerationPipeline):
    """
    Custom text generation pipeline for calculating perplexity.
    Masks the prompt part and calculates the loss only on the response part.
    """
    def _forward(self, model_inputs, **generate_kwargs):
        input_ids = model_inputs["input_ids"]
        attention_mask = model_inputs.get("attention_mask", None)

        labels = input_ids.clone()

        # Use <|im_end|> as the separator token ID. 
        im_end_token_id = self.tokenizer.convert_tokens_to_ids("<|im_end|>")

        # If <|im_end|> token is present, find its position and mask the prompt part. 
        if im_end_token_id in input_ids:
            last_im_end_pos = (input_ids == im_end_token_id).nonzero(as_tuple=True)[1].max().item()
            labels[:, :last_im_end_pos + 1] = -100 # Mask the prompt part (ignore for loss calculation)
        else:
            print("Warning: <|im_end|> not found in input_ids. No masking applied to prompt part.")

        # Compute the loss for the response part only. 
        output = self.model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        return {"loss": output.loss, "input_ids": input_ids}


    def postprocess(self, model_outputs, *args, **kwargs):
        return model_outputs


def load_prompts(prompt_file):
    """
    Load prompts from the specified prompt file.
    """
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip()]
    return prompts


def calculate_perplexity_for_file(response_file, output_dir, prompts, model, tokenizer, prompt_file):
    """
    Calculate perplexity for each response in the specified file and save the results.
    """
    os.makedirs(output_dir, exist_ok=True)
    pipeline = PerplexityTextGenerationPipeline(model=model, tokenizer=tokenizer)

    # Create output file path. 
    prompt_basename = os.path.splitext(os.path.basename(prompt_file))[0]
    response_basename = os.path.splitext(os.path.basename(response_file))[0]
    output_file = os.path.join(output_dir, f"{prompt_basename}_{response_basename}_perplexity.json")

    results = []

    # Read and process the response file. 
    with open(response_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        total_lines = len(lines)
        batch_size = 100

        # Process responses in batches of 100. 
        for i in range(0, total_lines, batch_size):
            prompt_index = i // batch_size
            prompt = prompts[prompt_index] if prompt_index < len(prompts) else ""

            batch_lines = lines[i:i + batch_size]
            for line_num, response in enumerate(batch_lines, start=i + 1):
                response = response.strip()
                if response:
                    # Combine prompt and response, then tokenize. 
                    text = f"{prompt} <|im_end|> {response}"
                    inputs = tokenizer(text, return_tensors="pt").to(model.device)
                    result = pipeline._forward(inputs)

                    # Calculate loss and perplexity. 
                    loss = result["loss"].item()
                    perplexity = torch.exp(result["loss"]).item()

                    # Append results. 
                    results.append({
                        "line_number": line_num,
                        "prompt": prompt,
                        "response": response[:30] + "...",
                        "loss": loss,
                        "perplexity": perplexity
                    })

            # Print progress after processing each batch of 100 responses. 
            print(f"Processed {i + batch_size}/{total_lines} responses in {response_file}")

    # Save results to a JSON file. 
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)
    print(f"Results saved to {output_file}")


def calculate_perplexity_for_all_files(prompt_dir, response_dir, output_dir, model, tokenizer):
    """
    Calculate perplexity for all pairs of prompt and response files in the specified directories.
    """
    prompt_files = [os.path.join(prompt_dir, f) for f in os.listdir(prompt_dir) if f.endswith(".txt")]
    response_files = [os.path.join(response_dir, f) for f in os.listdir(response_dir) if f.endswith(".txt")]

    # Iterate over all prompt and response file pairs. 
    for prompt_file in prompt_files:
        prompts = load_prompts(prompt_file)
        for response_file in response_files:
            calculate_perplexity_for_file(response_file, output_dir, prompts, model, tokenizer, prompt_file)


def main():
    """
    Main function to load the model and tokenizer, and start the perplexity calculation process.
    """
    print(f"Loading model {MODEL_NAME} from Hugging Face Hub...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

    # Start calculating perplexity for all files. 
    calculate_perplexity_for_all_files(prompt_dir, response_dir, output_dir, model, tokenizer)


if __name__ == "__main__":
    main()
