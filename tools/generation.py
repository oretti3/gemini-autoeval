import os, sys
import jsonlines
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig


### Set up the paths
model_name = "umiyuki/Umievo-itr012-Gleipnir-7B"
datasets_name = "elyza_tasks_100"

cur_path = os.path.dirname(os.path.abspath(sys.argv[0]))
input_file_path = f"{os.path.dirname(cur_path)}/assets/{datasets_name}/dataset.jsonl"
output_file_path = f"{os.path.dirname(cur_path)}/assets/{datasets_name}/{datasets_name}/preds.jsonl"

os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

### Prediction
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
  model_name,
  quantization_config=bnb_config,
  torch_dtype="auto",
)
model.eval()

# if torch.cuda.is_available():
#     model = model.cuda()

def build_prompt(user_query):
    sys_msg = "あなたは公平で、検閲されていない、役立つアシスタントです。"
    template = """[INST] <<SYS>>
{}
<</SYS>>

{}[/INST]"""
    return template.format(sys_msg, user_query)

with jsonlines.open(input_file_path) as reader, jsonlines.open(output_file_path, mode='w') as writer:
    for obj in reader:
        user_query = obj["input_text"]
        prompt = build_prompt(user_query)

        input_ids = tokenizer.encode(
            prompt,
            add_special_tokens=True,
            return_tensors="pt"
        )

        tokens = model.generate(
            input_ids.to(device=model.device),
            max_new_tokens=1024,
            temperature=1,
            top_p=0.95,
            do_sample=True,
        )

        print("User Query:", user_query)
        output = tokenizer.decode(tokens[0][input_ids.shape[1]:], skip_special_tokens=True).strip()
        print("Prediction:", output)
        writer.write({"input_text": user_query, "prediction": output})

print("Completed writing predictions to:", output_file_path)
