from __future__ import annotations
from ..models import LLM

def cot_outline(llm: LLM, query: str) -> str:
    prompt = f"Draft a short outline (3-6 bullets) of how to answer: {query}. Keep bullets concise."
    return llm.generate(prompt, system="Produce only bullets, no fluff.")
