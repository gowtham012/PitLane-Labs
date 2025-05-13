#!/usr/bin/env python3
import re, json
from dotenv import load_dotenv
from agent.rag_qa import answer_query
from agent.cad_integration import create_parametric_model

def parse_input(raw: str):
    """
    Splits user input into (query, design_params).
    design_params is a dict if JSON or free‑form params found, else None.
    """
    raw = raw.strip()

    # 1) Explicit JSON via "||"
    if "||" in raw:
        q_part, p_part = raw.split("||", 1)
        try:
            return q_part.strip(), json.loads(p_part.strip())
        except json.JSONDecodeError:
            return raw, None

    # 2) Trailing {...} JSON
    m = re.search(r'(\{[\s\S]*\})\s*$', raw)
    if m:
        try:
            params = json.loads(m.group(1))
            query = raw[:m.start()].strip()
            return query, params
        except json.JSONDecodeError:
            pass

    # 3) Free‑form "value key" pairs, e.g. "75 inner_diameter"
    pairs = re.findall(r'(\d+(?:\.\d+)?)\s*([A-Za-z_]+)', raw)
    if pairs:
        params = {}
        for val, key in pairs:
            params[key] = float(val) if '.' in val else int(val)
        # strip those pairs from the query
        query = re.sub(r'(\d+(?:\.\d+)?\s*[A-Za-z_]+[, ]*)+', '', raw).strip()
        return query, params

    return raw, None

def collect_params(query: str):
    """
    Interactively ask the user for design parameters until valid JSON is provided
    or user skips.
    """
    print("❔ I need design parameters to generate the CAD model.")
    print("  Please provide key dimensions and values.")
    print("  e.g. {\"stroke\":86, \"bore\":52}  or  stroke=86 bore=52")
    while True:
        resp = input(">> ").strip()
        if not resp:
            return None
        # try JSON
        try:
            return json.loads(resp)
        except json.JSONDecodeError:
            # try free‑form parsing
            _, params = parse_input(resp)
            if params:
                return params
        print("❌ Couldn't parse parameters. Please try again or press Enter to skip CAD.")

def main():
    load_dotenv()
    print("🚗 AutoRAG Engineer Agent (type 'exit' to quit)\n")

    while True:
        try:
            raw = input(">> ").strip()
            if not raw or raw.lower() in ("exit", "quit"):
                print("👋 Goodbye!")
                break

            query, design_params = parse_input(raw)

            # Always compute & display the text procedure
            print("\n🔧 Computing engineering procedure...\n")
            procedure = answer_query(query)
            print(procedure, "\n")

            # If it's a design request, ensure we have params
            if query.lower().startswith("design"):
                if design_params is None:
                    # Ask follow‑up until we get them (or user skips)
                    design_params = collect_params(query)

                if design_params:
                    try:
                        link = create_parametric_model(design_params)
                        print(f"🔗 CAD Model Generated: {link}\n")
                    except Exception as e:
                        print(f"⚠️  CAD generation failed: {e}\n")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"[Error] {e}\n")

if __name__ == "__main__":
    main()
