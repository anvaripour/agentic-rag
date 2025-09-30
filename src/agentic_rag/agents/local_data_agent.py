from __future__ import annotations
from typing import List, Tuple
from ..memory import LongTermMemory
from ..config import USE_MCP
from ..mcp.client import MCPClient
import os

class LocalDataAgent:
    def __init__(self, ltm: LongTermMemory):
        self.ltm = ltm
		self.mcp_client = MCPClient([sys.executable, "-m", "agentic_rag.mcp.servers.local_pdf_server"]) if USE_MCP else None

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
		if self.mcp_client:
            resp = self.mcp_client.request("search", {"query": query, "k": k})
            return resp.get("results", [])
        return self.ltm.search(query, k=k)
