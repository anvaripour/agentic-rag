from __future__ import annotations
from typing import Dict, Any, List
from ..memory import ShortTermMemory, LongTermMemory
from ..models import LLM
from ..planners.react import react_plan
from ..planners.cot import cot_outline
from .local_data_agent import LocalDataAgent
from .search_agent import SearchAgent
from .cloud_agent import CloudAgent

class AggregatorAgent:
    def __init__(self, stm: ShortTermMemory, ltm: LongTermMemory):
        self.stm = stm
        self.ltm = ltm
        self.llm = LLM()
        self.local_agent = LocalDataAgent(self.ltm)
        self.search_agent = SearchAgent()
        self.cloud_agent = CloudAgent()

    def handle(self, query: str) -> Dict[str, Any]:
        self.stm.add("user", query)
        outline = cot_outline(self.llm, query)
        steps = react_plan(query)

        traces: List[Dict[str, Any]] = []
        scratch: List[str] = []

        for step in steps:
            tool, arg = step["tool"], step["input"]
            if tool == "local":
                docs = self.local_agent.retrieve(arg)
                traces.append({"tool": "local", "results": docs})
                scratch.append("\n".join([d[0] for d in docs]))
            elif tool == "search":
                hits = self.search_agent.search(arg)
                traces.append({"tool": "search", "results": hits})
                scratch.append("\n".join([h.get("snippet","") for h in hits]))
            elif tool == "cloud":
                res = self.cloud_agent.call(arg)
                traces.append({"tool": "cloud", "results": res})
                scratch.append(str(res))

        context = "\n\n".join(scratch)[:6000]
        prompt = (
            f"Question: {query}\n\n"
            f"Outline: {outline}\n\n"
            f"Context from tools (may be partial):\n{context}\n\n"
            f"Write a concise, cited answer. If unsure, say so."
        )
        answer = self.llm.generate(prompt, system="You synthesize tool outputs into clear answers with citations.")
        self.stm.add("assistant", answer)
        return {"answer": answer, "traces": traces, "outline": outline}
