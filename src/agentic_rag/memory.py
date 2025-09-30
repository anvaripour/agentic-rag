from __future__ import annotations
import time, os
from typing import List, Dict, Any, Optional, Tuple
from sqlitedict import SqliteDict

# ---------- Short-term memory (STM): rolling buffer on SQLite ----------
class ShortTermMemory:
    def __init__(self, db_path: str, namespace: str = "default", max_turns: int = 30):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db = SqliteDict(db_path, autocommit=True)
        self.ns = f"stm:{namespace}"
        self.max_turns = max_turns
        if self.ns not in self.db:
            self.db[self.ns] = []

    def add(self, role: str, content: str):
        trace = self.db[self.ns]
        trace.append({"role": role, "content": content, "ts": time.time()})
        self.db[self.ns] = trace[-self.max_turns:]

    def get(self) -> List[Dict[str, Any]]:
        return list(self.db[self.ns])

    def clear(self):
        self.db[self.ns] = []

# ---------- Long-term memory (LTM): FAISS over PDF chunks ----------
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

class LongTermMemory:
    def __init__(self, index_dir: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        self.emb = HuggingFaceEmbeddings(model_name=model_name)
        self.vs: Optional[FAISS] = None
        self._load()

    def _load(self):
        try:
            self.vs = FAISS.load_local(self.index_dir, self.emb, allow_dangerous_deserialization=True)
        except Exception:
            self.vs = None

    def is_empty(self) -> bool:
        return self.vs is None

    def create(self, docs: List[Document]):
        self.vs = FAISS.from_documents(docs, self.emb)
        self.vs.save_local(self.index_dir)

    def add(self, docs: List[Document]):
        if self.vs is None:
            self.create(docs)
        else:
            self.vs.add_documents(docs)
            self.vs.save_local(self.index_dir)

    def search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        if self.vs is None:
            return []
        res = self.vs.similarity_search_with_relevance_scores(query, k=k)
        return [(r[0].page_content, float(r[1])) for r in res]
