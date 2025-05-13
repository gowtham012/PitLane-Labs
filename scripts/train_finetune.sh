python - <<EOF
from agent.fine_tune import prepare_dataset
data = prepare_dataset("data/feedback_logs/feedback.jsonl")
with open("feedback_dataset.jsonl","w") as f:
    for r in data: f.write(json.dumps(r)+"\n")
EOF
# Call OpenAI fine-tune or HF
echo "Run your fine-tune job on feedback_dataset.jsonl"