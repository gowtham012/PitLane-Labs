# agent/hybrid_agent.py
from agent.rag_qa import retrieve_contexts, generate_answer

class HybridAgent:
    def __init__(self):
        pass

    def run(self, query: str, params=None):
        """
        For compatibility with evaluate_agent.py:
        - query: the question string
        - params: (ignored) additional params, if any
        Returns a tuple: (answer_text, contexts_list)
        """
        # 1) Retrieve contexts
        contexts = retrieve_contexts(query)
        # 2) Generate the final answer
        answer = generate_answer(query, contexts)
        # 3) Return both
        return answer, contexts
