from __future__ import annotations
import httpx
from typing import List, Dict, Any
from ..config import GOOGLE_CSE_ID, GOOGLE_API_KEY

class SearchAgent:
    def __init__(self):
        self.cx = GOOGLE_CSE_ID
        self.key = GOOGLE_API_KEY

    def search(self, query: str, num: int = 5) -> List[Dict[str, Any]]:
        if not (self.cx and self.key):
            return []  # offline stub
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"q": query, "cx": self.cx, "key": self.key, "num": num}
        r = httpx.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        return [
            {"title": it.get("title"), "link": it.get("link"), "snippet": it.get("snippet")}
            for it in data.get("items", [])
        ]
