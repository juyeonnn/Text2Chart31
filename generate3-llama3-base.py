from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import torch
import json
import os

def save_to_json(data, filename="output/task3-llama3-8b-instruct.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

model_name = "meta-llama/Meta-Llama-3-8B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=False,
    device_map="auto",
    torch_dtype=torch.bfloat16,
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

with open("./prepare-data/Text2Chart-31-test.json", "r") as file:
    test_set = json.load(file)

total_num = len(test_set)

# Print elapsed hour/min/sec
start = time.time()

dataset = []
def print_elapsed_time(start):
    elapsed = time.time() - start
    # format as 00:00:00
    print(f"=== Elapsed time: {time.strftime('%H:%M:%S', time.gmtime(elapsed))} ===")


for index, item in enumerate(test_set):
    input_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are good at describing about the given data visualization code.
Make sure when you describe a graph, mention the data points or csv file that are going to be used; otherwise, we won't be able to sketch the graph.
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Your task is to generate a description of the chart based on the provided code, 
please make sure to include labels from the graph. 

Code:
“””Python
{item['code'] + ' ' if item['code'] else ''}

Please generate the corresponding description.

<|eot_id|><|start_header_id|>assistant<|end_header_id|>
Description:
"""
    input_tokens = tokenizer(input_prompt, return_tensors="pt")["input_ids"].to("cuda")
    generated_output = model.generate(
        input_ids=input_tokens,
        do_sample=True,
        top_k=10,
        temperature=0.1,
        top_p=0.95,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        max_length=2048,
    )
    value = tokenizer.decode(generated_output[0], skip_special_tokens=True)
    print(value)
    print(f"=== Step: ({index} / {total_num}) ===")
    print_elapsed_time(start)
    dataset.append(
        {
            "id": item["id"],
            "description": item["description"],
            "generated_output": value,
            "code": item["code"],
        }
    )
    save_to_json(dataset)
