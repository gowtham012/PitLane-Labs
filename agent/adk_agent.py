# agent/adk_agent.py
from adk import Agent
from agent.rag_qa import answer_query

class AutoRagAgent(Agent):
    async def run(self, input_text: str) -> str:
        return answer_query(input_text)

if __name__ == "__main__":
    Agent.launch(__file__)
