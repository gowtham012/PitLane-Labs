# # agent/rag_qa.py  ─────────────  v2 – “full-detail” engineering answers
# import os, json, re
# from typing import List, Dict
# import numpy as np
# import faiss
# from dotenv import load_dotenv
# from openai import OpenAI

# # ───────────────────────────────────────────────────────────────────────
# # 1.  ENV / CLIENT
# # ───────────────────────────────────────────────────────────────────────
# load_dotenv()
# EMB_DIR       = os.getenv("EMBEDDINGS_DIR", "./embeddings")
# TOP_K         = int(os.getenv("RETRIEVAL_TOP_K", 4))
# EMBED_MODEL   = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
# LLM_MODEL     = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
# OPENAI_KEY    = os.getenv("OPENAI_API_KEY")

# if not OPENAI_KEY:
#     raise RuntimeError("OPENAI_API_KEY must be set in .env")

# client = OpenAI(api_key=OPENAI_KEY)

# faiss_idx  = faiss.read_index(os.path.join(EMB_DIR, "index.faiss"))
# with open(os.path.join(EMB_DIR, "chunks.json"), encoding="utf-8") as fp:
#     CHUNKS: List[Dict] = json.load(fp)

# # ───────────────────────────────────────────────────────────────────────
# # 2.  HELPERS
# # ───────────────────────────────────────────────────────────────────────
# def _embed(txt: str) -> np.ndarray:
#     vec = client.embeddings.create(input=[txt], model=EMBED_MODEL).data[0].embedding
#     return np.asarray(vec, dtype="float32")

# def _retrieve(q: str, k: int = TOP_K) -> List[str]:
#     D, I = faiss_idx.search(_embed(q)[None, :], k)
#     return [CHUNKS[i]["text"] for i in I[0]]

# # “super-template” prompt that mimics your sample answer
# _SYSTEM_PROMPT = """
# You are a helpful assistant that provides detailed engineering design
#     "You are a senior automotive engineer with hands-on design experience. "
#     "Provide a concise, numbered, real-world procedure so a junior engineer can "
#     "immediately implement it. "
#     "**If a required value is missing, assume a conservative industry-standard "
#     "default and continue – do NOT keep asking the user.**"

# ---
# Below is a practical, production-oriented set of geometry and material targets
# you can drop straight into a CAD model (STEP, IGES, or parametric) for the
# requested component.

# ## 1.  Layout & bearing (or configuration) scheme
#   • A Markdown table with Item | Spec | Rationale

# ## 2.  Fundamental geometry
#   • Table “Parameter | Value | How it’s obtained”

# ## 3.  Web / counterweight / sealing / skirt … (section name depends on device)
#   • Second detailed table

# ## 4.  Overall stack-up
#   • Table Segment | Length(mm) | Comment with TOTAL length line at bottom

# ## 5.  Oil (or lube / cooling / sealing) drillings
#   • Short bullet list (≤ 4 bullets)

# ## 6.  Material & heat-treat
#   • Two-column table Step | Spec

# ## 7.  Quick ASCII reference drawing
#   • 5-10 line monospace sketch

# ## 8.  Strength (or thermals) sanity checks
#   • Table Check | Result

# ### How to use these numbers
#   • 3–5 ordered steps

# ### Question
# **Would you like a cloud-CAD model for this design? (yes/no)**

# If ANY obligatory dimension or parameter is missing
# (e.g. stroke, bore, power, pressure) you must first ask
# a concise follow-up question **instead of** producing the template.
# Never invent critical numbers.
# """

# def _generate_answer(task: str, ctx: List[str]) -> str:
#     user_msg = f"""Request:\n{task}\n\nContext snippets (reference only):\n""" + \
#                "".join(f"- {c[:350]}\n" for c in ctx)
#     chat = client.chat.completions.create(
#         model            = LLM_MODEL,
#         temperature      = 0.0,
#         top_p            = 1.0,
#         max_tokens       = 1000,
#         messages=[
#             {"role": "system", "content": _SYSTEM_PROMPT},
#             {"role": "user",   "content": user_msg}
#         ],
#     )
#     return chat.choices[0].message.content.strip()

# # ───────────────────────────────────────────────────────────────────────
# # 3.  PUBLIC
# # ───────────────────────────────────────────────────────────────────────
# def answer_query(user_input: str) -> str:
#     """
#     Main entry – returns the LLM answer (may be a follow-up question
#     if key data are missing).
#     """
#     ctx = _retrieve(user_input)
#     return _generate_answer(user_input, ctx)

# # ───────────────────────────────────────────────────────────────────────
# # 4.  Dimension-scraper (for your CAD hand-off)
# # ───────────────────────────────────────────────────────────────────────
# _DIM_RX = re.compile(
#     r"([A-Za-z0-9_./ −–]+?)\s*(?:≈|=|:)\s*([0-9]+(?:\.[0-9]+)?)\s*(mm|cm|°|deg|rpm|kN|Nm|N·m|MPa)?",
#     re.I
# )

# def extract_dimensions(ans_block: str) -> Dict[str, float]:
#     """
#     Parse “Dimensions for design” or any table into {key : value_mm}.
#     Rudimentary – extend as needed.
#     """
#     dims: Dict[str, float] = {}
#     for name, num, unit in _DIM_RX.findall(ans_block):
#         key = name.strip().lower().replace(" ", "_")
#         val = float(num)
#         unit = (unit or "").lower()
#         if unit == "cm":
#             val *= 10
#         dims[key] = val
#     return dims

# __all__ = ["answer_query", "extract_dimensions"]








# agent/rag_qa.py
"""
Hybrid RAG pipeline
───────────────────
• 80 % context → local FAISS chunks (‘book knowledge’)
• 20 % context → on-the-fly web snippets (‘internet knowledge’)
• LLM prompt template that explicitly lists every numeric design
  seed we already scraped so the model does *not* re-ask the user.
"""

from __future__ import annotations
import os, json, re, time
from typing import List, Dict

import numpy as np
import faiss
from dotenv import load_dotenv
from openai import OpenAI

# ────────────────────────── Config ──────────────────────────
load_dotenv()
EMB_DIR        = os.getenv("EMBEDDINGS_DIR", "./embeddings")
TOP_K_LOCAL    = int(os.getenv("RETRIEVAL_TOP_K", 5))   # chunks from PDF corpus
TOP_K_WEB      = int(os.getenv("WEB_TOP_K",        3))  # snippets from live web
EMBED_MODEL    = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
LLM_MODEL      = os.getenv("OPENAI_LLM_MODEL",   "gpt-4o-mini")
API_KEY        = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise EnvironmentError("OPENAI_API_KEY missing in .env")

client = OpenAI(api_key=API_KEY)

# ──────────────────────── Local corpus ──────────────────────
_index_path  = os.path.join(EMB_DIR, "index.faiss")
_chunks_path = os.path.join(EMB_DIR, "chunks.json")
if not (os.path.exists(_index_path) and os.path.exists(_chunks_path)):
    raise FileNotFoundError("FAISS index or chunks.json not found; run embeddings/build_index.py")

_index  = faiss.read_index(_index_path)
_chunks = json.load(open(_chunks_path, encoding="utf-8"))

def _retrieve_local(query: str, k: int) -> List[str]:
    """Top-k chunks from local vector store."""
    q_emb = client.embeddings.create(input=[query], model=EMBED_MODEL).data[0].embedding
    D, I  = _index.search(np.array([q_emb], dtype="float32"), k)
    return [_chunks[i]["text"] for i in I[0]]

# ───────────────────────── Web search ───────────────────────
def _search_web(query: str, k: int) -> List[str]:
    """
    Very light-weight web retriever (uses this platform’s `web.run`).
    Returns k “title – snippet” strings. Falls back to [] offline.
    """
    try:
        import web  # runtime-injected tool
        ids = web.run({
            "search_query": [{"q": query, "recency": None, "domains": None}],
            "response_length": "short"
        })
        # ids is a list of search sources. pick first result block
        first = ids[0]
        hits  = first["results"][:k]
        snippets = [f"{h['title']} – {h['snippet']}" for h in hits]
        return snippets
    except Exception:
        return []          # no internet in this environment

# ────────────────── Helper: prettify seed numbers ───────────
_num_rx = re.compile(r"([a-z0-9_]+)=([^;,\n]+)", re.I)
def _dict_to_bullets(d: Dict[str, str]) -> str:
    return "\n".join([f"• {k}: {v}" for k, v in d.items()])

# ─────────────────── Main public function ───────────────────
def answer_query(
    query: str,
    allow_web: bool = True,
    **design_data
) -> str:
    """
    Parameters
    ----------
    query : str
        The raw user request (e.g. “design a crankshaft …”)
    allow_web : bool, optional
        If False we skip the live search step (user said “don’t search”).
    **design_data : Any
        Arbitrary scraped numbers e.g. bore=79, stroke=54.3; passed
        in by chat_agent so the LLM doesn’t ask again.
    """
    # 1) Retrieve contexts
    local_ctx = _retrieve_local(query, TOP_K_LOCAL)
    web_ctx   = _search_web(query, TOP_K_WEB) if allow_web else []
    # Weight: keep 80 % local, 20 % web (already enforced via k-values)

    # 2) Build prompt
    seed_section = _dict_to_bullets(design_data) if design_data else "—"
    contexts = "\n\n".join(
        [f"[BOOK{i+1}] {c}"   for i, c in enumerate(local_ctx)] +
        [f"[WEB{i+1}]  {s}"   for i, s in enumerate(web_ctx)]
    )

    messages = [
        {
            "role": "system",
            "content":
            "You are an expert automotive design engineer assistant.\n"
            "When you receive a 'Design X' request always reply in **exactly** "
            "this structure:\n"
            "1. **Process of design** – step-by-step practical procedure\n"
            "2. **Dimensions for design** – bullet or table of numeric values\n"
            "3. **Question:** 'Would you like a cloud-CAD model for this design? (yes/no)'\n"
            "Use the contexts below for 80 % of your factual content; "
            "you may add minor reasoning or interpolation but **do not** ask "
            "the user to re-enter values that already exist in the seed list."
        },
        {
            "role": "user",
            "content":
            f"### User request\n{query}\n\n"
            f"### Known numeric parameters (parsed)\n{seed_section}\n\n"
            f"### Context library\n{contexts}"
        }
    ]

    # 3) Call LLM
    resp = client.chat.completions.create(
        model            = LLM_MODEL,
        messages         = messages,
        temperature      = 0.15,
        top_p            = 1,
        frequency_penalty= 0.0,
        presence_penalty = 0.0,
        max_tokens       = 900
    )
    return resp.choices[0].message.content.strip()

# convenience wrapper for chat_agent
def generate_answer(query: str, contexts: List[str]) -> str:  # kept for compatibility
    return answer_query(query)

def retrieve_contexts(query: str) -> List[str]:   # ditto
    return _retrieve_local(query, TOP_K_LOCAL)

__all__ = ["answer_query", "retrieve_contexts", "generate_answer"]
