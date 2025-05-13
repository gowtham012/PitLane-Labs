from dotenv import load_dotenv
import os
import fitz  # PyMuPDF

# 1. Load env
load_dotenv()
DATA_DIR = os.getenv("DATA_DIR", "./data")
INGEST_DIR = os.getenv("INGEST_OUTPUT_DIR", "./ingest")

# 2. Ensure output dir
os.makedirs(INGEST_DIR, exist_ok=True)

# 3. Iterate PDFs
for fname in os.listdir(DATA_DIR):
    if not fname.lower().endswith(".pdf"):
        continue
    pdf_path = os.path.join(DATA_DIR, fname)
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()

    out_name = os.path.splitext(fname)[0] + ".txt"
    out_path = os.path.join(INGEST_DIR, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[✓] Extracted {fname} → {out_path}")