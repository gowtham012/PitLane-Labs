import json

def prepare_dataset(feedback_file: str) -> list[dict]:
    data = []
    with open(feedback_file, 'r') as f:
        for line in f:
            rec = json.loads(line)
            data.append({"prompt": rec['query'], "completion": rec['correction'] or rec['response']})
    return data

def train_lora(dataset_path: str):
    # Hook into HF or OpenAI fine-tune
    print(f"Fine-tuning on {dataset_path}")