#!/usr/bin/env python3
import os
import json
import time
import logging

import numpy as np
import faiss
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI

# ─── Configure Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


def main():
    # ─── 1. Load environment variables ────────────────────────────────────────────
    load_dotenv()
    INGEST_DIR       = os.getenv("INGEST_OUTPUT_DIR", "./ingest")
    EMBEDDINGS_DIR   = os.getenv("EMBEDDINGS_DIR", "./embeddings")
    CHUNK_SIZE       = int(os.getenv("CHUNK_SIZE", 400))
    CHUNK_OVERLAP    = int(os.getenv("CHUNK_OVERLAP", 50))
    EMBED_MODEL      = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
    BATCH_SIZE       = int(os.getenv("EMBED_BATCH_SIZE", 100))
    OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")

    if not OPENAI_API_KEY:
        logger.error("Environment variable OPENAI_API_KEY is not set.")
        return

    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Ensure output directory exists
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

    # Log configuration
    logger.info(f"INGEST_DIR       = {INGEST_DIR}")
    logger.info(f"EMBEDDINGS_DIR   = {EMBEDDINGS_DIR}")
    logger.info(f"CHUNK_SIZE       = {CHUNK_SIZE}")
    logger.info(f"CHUNK_OVERLAP    = {CHUNK_OVERLAP}")
    logger.info(f"EMBED_MODEL      = {EMBED_MODEL}")
    logger.info(f"BATCH_SIZE       = {BATCH_SIZE}")

    # ─── 2. Read & chunk all extracted text files ─────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    all_chunks = []
    for fname in os.listdir(INGEST_DIR):
        if not fname.lower().endswith(".txt"):
            continue
        path = os.path.join(INGEST_DIR, fname)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        chunks = splitter.split_text(text)
        for chunk in chunks:
            all_chunks.append({"text": chunk, "source": fname})

    logger.info(f"[+] Prepared {len(all_chunks)} text chunks")

    # ─── 3. Embed chunks via OpenAI client (batched) ──────────────────────────────
    embeddings = []
    total_batches = (len(all_chunks) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_idx in range(total_batches):
        start = batch_idx * BATCH_SIZE
        end   = min(start + BATCH_SIZE, len(all_chunks))
        batch = all_chunks[start:end]
        texts = [c["text"] for c in batch]

        try:
            response = client.embeddings.create(
                input=texts,
                model=EMBED_MODEL
            )
        except Exception as e:
            logger.error(f"Embedding API error on batch {batch_idx+1}: {e}")
            return

        # Collect embeddings
        for data in response.data:
            embeddings.append(data.embedding)

        logger.info(f"[+] Embedded batch {batch_idx+1} of {total_batches}")
        time.sleep(0.2)  # brief pause to respect rate limits

    embs = np.array(embeddings, dtype="float32")
    logger.info(f"[+] Created embedding matrix of shape {embs.shape}")

    # ─── 4. Build FAISS index & save ───────────────────────────────────────────────
    dim = embs.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embs)
    index_path = os.path.join(EMBEDDINGS_DIR, "index.faiss")
    faiss.write_index(index, index_path)
    logger.info(f"[✓] FAISS index saved to {index_path}")

    # ─── 5. Persist chunk metadata ────────────────────────────────────────────────
    chunks_path = os.path.join(EMBEDDINGS_DIR, "chunks.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    logger.info(f"[✓] Chunk metadata saved to {chunks_path}")


if __name__ == "__main__":
    main()
