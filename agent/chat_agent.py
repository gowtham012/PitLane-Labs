# agent/chat_agent.py
"""
Tiny conversational loop around the hybrid RAG engine.
──────────────────────────────────────────────────────
 • Detects whether the user’s message is a *design* request
   (“design a crankshaft …”, “design piston-ring …”, etc.)
 • Scrapes every numeric seed it can find (bore, stroke, rpm …)
   so the LLM never asks again.
 • Feeds those seeds into rag_qa.answer_query(**design_data)
   which already formats the three-section output:
     1. Process of design
     2. Dimensions for design
     3. CAD offer question
 • If the user replies “yes”, we call create_parametric_model()
   and print the returned Onshape URL.
"""

import re, sys, json
from pathlib import Path

# Internal modules
from agent.rag_qa          import answer_query
from agent.cad_integration import create_parametric_model   # you built this earlier

# ─────────────────── regex helpers ────────────────────
NUM_KV_RX = re.compile(
    r"(?P<key>[a-z][a-z0-9 _\-]*?)\s*[:=]\s*(?P<val>[-+]?\d*\.?\d+)"
    r"\s*(?P<unit>mm|cm|rpm|hp|kW|Nm|bar|psi|kg|°|deg|inch|in|lb-ft)?",
    re.I
)

def scrape_numbers(text: str) -> dict:
    """Return {key: 'value unit'} for every k=v found in the text."""
    out = {}
    for m in NUM_KV_RX.finditer(text):
        key  = m.group("key").strip().lower().replace(" ", "_")
        val  = m.group("val")
        unit = m.group("unit") or ""
        out[key] = f"{val} {unit}".strip()
    return out

def is_design_prompt(txt: str) -> bool:
    return bool(re.match(r"\s*design\b", txt, re.I))

# ──────────────────── simple REPL ─────────────────────
def main():
    print("🏁  Engineering Chat – type 'exit' to quit\n")
    while True:
        try:
            user = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not user:
            continue
        if user.lower() in {"exit", "quit"}:
            break

        # 1) parse seeds
        seeds = scrape_numbers(user)
        # 2) ask the RAG engine
        reply = answer_query(user, allow_web=True, **seeds)
        print("\n🤖", reply, "\n")

        # 3) If design prompt, handle CAD follow-up
        if is_design_prompt(user):
            ans = ""
            while ans.lower() not in {"yes", "no"}:
                ans = input("🖥  Would you like a cloud-CAD model for this design? (yes/no) ").strip()
            if ans.lower() == "yes":
                try:
                    url = create_parametric_model(seeds)
                    print(f"🔗  Your Onshape model: {url}\n")
                except Exception as e:
                    print(f"⚠️  CAD generation failed: {e}\n")

if __name__ == "__main__":
    main()
