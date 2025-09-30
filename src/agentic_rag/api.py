from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel
from .config import MEMORY_DB, INDEX_DIR
from .memory import ShortTermMemory, LongTermMemory
from .agents.aggregator import AggregatorAgent
from .graph import build_agentic_graph

app = FastAPI(title="Agentic RAG API")

stm = ShortTermMemory(MEMORY_DB, namespace="default", max_turns=40)
ltm = LongTermMemory(INDEX_DIR)
agg = AggregatorAgent(stm, ltm)

class QueryIn(BaseModel):
    query: str

@app.post("/query_graph")
def query_graph(inp: QueryIn):
    result = graph.invoke({"query": inp.query, **deps})
    return {"answer": result["answer"], "traces": result.get("traces", []), "outline": result.get("outline", "")}

@app.get("/healthz")
def health():
    return {"ok": True}
