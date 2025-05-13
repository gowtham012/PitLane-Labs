import sys
import os
# Add project root to sys.path so the agent package is found
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import json
import argparse
from agent.hybrid_agent import HybridAgent
from agent.rag_qa import retrieve_contexts, generate_answer as baseline_answer

# Load sample queries and expected outputs (if available)
def load_suite(path):
    with open(path, 'r') as f:
        return json.load(f)

# Run evaluation suite
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate AutoRAG Agent')
    parser.add_argument('--suite', type=str, default='scripts/eval_suite.json',
                        help='Path to JSON file of test tasks')
    parser.add_argument('--output', type=str, default='scripts/eval_results.jsonl',
                        help='Results log')
    args = parser.parse_args()

    suite = load_suite(args.suite)
    agent = HybridAgent()

    with open(args.output, 'w', encoding='utf-8') as out:
        for item in suite:
            task = item['task']
            params = item.get('params')
            print(f"Evaluating: {task}")
            text, _ = agent.run(task, params)
            # If expected answer available, compute simple BLEU or exact match
            expected = item.get('expected')
            result = {
                'task': task,
                'response': text,
                'expected': expected
            }
            out.write(json.dumps(result) + '')
    print(f"Evaluation complete. Results in {args.output}")