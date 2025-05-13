#!/usr/bin/env python3
import os
import json
import sys
import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# ─── 1. Load env vars ───────────────────────────────────────────────────────────
load_dotenv()  # reads .env in cwd

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: OPENAI_API_KEY is not set. Please add it to your .env or export it.", file=sys.stderr)
    sys.exit(1)

# ─── 2. Initialize OpenAI client ───────────────────────────────────────────────
client = OpenAI(api_key=API_KEY)

# ─── 3. Load FAISS index & chunks ───────────────────────────────────────────────
EMB_DIR   = "./embeddings"
INDEX_FP  = os.path.join(EMB_DIR, "index.faiss")
CHUNKS_FP = os.path.join(EMB_DIR, "chunks.json")

if not os.path.exists(INDEX_FP) or not os.path.exists(CHUNKS_FP):
    print(f"ERROR: Missing index or chunks file in {EMB_DIR}", file=sys.stderr)
    sys.exit(1)

index  = faiss.read_index(INDEX_FP)
chunks = json.load(open(CHUNKS_FP, encoding="utf-8"))

# ─── 4. Helper: embed a single query ────────────────────────────────────────────
def embed_query(text: str) -> np.ndarray:
    resp = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    emb = resp.data[0].embedding
    return np.array(emb, dtype="float32")

# ─── 5. Run test retrieval ──────────────────────────────────────────────────────
query = "How to design an crankshaft?"
q_emb = embed_query(query)

# find top 3
D, I = index.search(np.expand_dims(q_emb, 0), k=3)

print(f"Query: {query}\n")
for rank, idx in enumerate(I[0], start=1):
    src = chunks[idx]["source"]
    snippet = chunks[idx]["text"].replace("\n", " ")[:300]
    print(f"--- Result {rank} (source: {src}) ---")
    print(snippet + "...\n")
