from __future__ import annotations
from typing import List, Dict

def react_plan(query: str) -> List[Dict]:
    q = query.lower()
    steps: List[Dict] = []
    # Heuristic: local PDFs first; add web search for "latest/recent/2024/2025";
    # call GCP tools if query mentions gcp/cloud.
    steps.append({"tool": "local", "input": query})
    if any(w in q for w in ["latest", "recent", "2024", "2025", "news", "paper"]):
        steps.append({"tool": "search", "input": query})
    if any(w in q for w in ["gcp", "bucket", "vertex", "cloud"]):
        steps.append({"tool": "cloud", "input": "summarize cloud resources relevant to: " + query})
    return steps
