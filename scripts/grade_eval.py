#!/usr/bin/env python3
import json
import pandas as pd
import os
import re

# 1. Read the raw file and fix missing newlines
results_path = "scripts/eval_results.jsonl"
if not os.path.exists(results_path):
    raise FileNotFoundError(f"Couldn’t find {results_path}")

raw = open(results_path, encoding="utf-8").read()
# Insert newline between concatenated JSON objects
fixed = re.sub(r'\}\s*\{', '}\n{', raw)

# 2. Parse each JSON object
records = []
for line in fixed.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        rec = json.loads(line)
    except json.JSONDecodeError as e:
        print(f"[Warning] Skipping invalid JSON line: {e}")
        continue
    records.append(rec)

# 3. Build DataFrame
df = pd.DataFrame(records)

# 4. Grade correctness based on "expected" field
def check_match(row):
    exp = row.get("expected")
    resp = row.get("response", "")
    if exp:
        return exp.strip() in resp
    else:
        return None

df["correct"] = df.apply(check_match, axis=1)

# 5. Summary metrics
total = len(df)
with_expected = df["correct"].notnull().sum()
correct = df["correct"].sum() or 0

print(f"Total tasks tested:      {total}")
print(f"Tasks with gold answer:  {with_expected}")
print(f"Correct matches:         {correct} ({(correct/with_expected*100) if with_expected else 0:.0f}% pass‑rate)\n")

print("Details:")
print(df[["task", "correct"]].to_string(index=False))
