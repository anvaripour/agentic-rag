from __future__ import annotations
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from .memory import ShortTermMemory, LongTermMemory
from .models import LLM
from .planners.react import react_plan
from .planners.cot import cot_outline
from .agents.local_data_agent import LocalDataAgent
from .agents.search_agent import SearchAgent
from .agents.cloud_agent import CloudAgent
from .config import MEMORY_DB, INDEX_DIR

# ---------- Shared State ----------
class AgenticState(dict):
    query: str
    outline: str
    plan: list
    step: int
    traces: list
    answer: str

# ---------- Node definitions ----------
def planner_node(state: AgenticState) -> AgenticState:
    llm = state["llm"]
    stm = state["stm"]

    # Save user query
    stm.add("user", state["query"])

    outline = cot_outline(llm, state["query"])
    steps = react_plan(state["query"])

    # Save planner outline
    stm.add("assistant", f"[Planner Outline]\n{outline}")

    return {**state, "outline": outline, "plan": steps, "step": 0, "traces": []}


def tool_node(state: AgenticState) -> AgenticState:
    steps = state["plan"]
    idx = state["step"]
    stm = state["stm"]

    if idx >= len(steps):
        return state

    step = steps[idx]
    tool, arg = step["tool"], step["input"]
    traces = state.get("traces", [])

    if tool == "local":
        docs = state["local_agent"].retrieve(arg)
        traces.append({"tool": "local", "results": docs})
        stm.add("assistant", f"[Local Results] {str(docs[:2])} ...")
    elif tool == "search":
        hits = state["search_agent"].search(arg)
        traces.append({"tool": "search", "results": hits})
        stm.add("assistant", f"[Search Results] {str(hits[:2])} ...")
    elif tool == "cloud":
        res = state["cloud_agent"].call(arg)
        traces.append({"tool": "cloud", "results": res})
        stm.add("assistant", f"[Cloud Result] {res}")

    return {**state, "traces": traces, "step": idx + 1}


def tool_router(state: AgenticState) -> str:
    if state["step"] < len(state["plan"]):
        return "tool"
    return "answer"


def answer_node(state: AgenticState) -> AgenticState:
    llm = state["llm"]
    stm = state["stm"]

    context = "\n\n".join([str(t["results"]) for t in state.get("traces", [])])
    prompt = (
        f"Question: {state['query']}\n\n"
        f"Outline: {state['outline']}\n\n"
        f"Context from tools (may be partial):\n{context}\n\n"
        f"Write a concise, cited answer. If unsure, say so."
    )
    ans = llm.generate(prompt, system="You synthesize tool outputs into clear answers with citations.")

    # Save final answer
    stm.add("assistant", ans)

    return {**state, "answer": ans}

# ---------- Graph factory ----------
def build_agentic_graph():
    stm = ShortTermMemory(MEMORY_DB, namespace="default", max_turns=40)
    ltm = LongTermMemory(INDEX_DIR)
    llm = LLM()
    local_agent = LocalDataAgent(ltm)
    search_agent = SearchAgent()
    cloud_agent = CloudAgent()

    builder = StateGraph(AgenticState)

    builder.add_node("plan", planner_node)
    builder.add_node("tool", tool_node)
    builder.add_node("answer", answer_node)

    builder.set_entry_point("plan")

    # Conditional loop: keep running tools until plan done → answer
    builder.add_conditional_edges("tool", tool_router, {"tool": "tool", "answer": "answer"})
    builder.add_edge("plan", "tool")
    builder.add_edge("answer", END)

    memory = SqliteSaver.from_conn_string(f"sqlite:///{MEMORY_DB}")
    graph = builder.compile(checkpointer=memory)

    return graph, {
        "llm": llm,
        "stm": stm,   # <-- STM injected into state
        "local_agent": local_agent,
        "search_agent": search_agent,
        "cloud_agent": cloud_agent,
    }
