def build_cot_prompt(task: str, contexts: list[str]) -> list[dict]:
    system = (
        "You are a top automotive engineer. "
        "Walk through your reasoning step by step: 1) evaluate load cases; 2) consider manufacturability; 3) optimize weight."
    )
    user = f"Design Task: {task}\n\nRelevant Excerpts:\n" + "\n".join(contexts)
    hint = (
        "Let’s think step by step:\n"
        "1. Load analysis...\n"
        "2. Material & manufacturing...\n"
        "3. Weight optimization..."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user",   "content": user},
        {"role": "assistant", "content": hint}
    ]