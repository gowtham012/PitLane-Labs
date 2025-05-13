import os, json
load_dotenv = None
FEEDBACK_PATH = os.getenv("FEEDBACK_PATH", "data/feedback_logs/feedback.jsonl")

def log_feedback(query: str, response: str, rating: int, correction: str=None):
    os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)
    entry = {"query":query, "response":response, "rating":rating, "correction":correction}
    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")