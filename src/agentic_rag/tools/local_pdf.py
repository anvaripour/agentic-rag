from __future__ import annotations
import argparse, os, glob
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from ..memory import LongTermMemory
from ..config import INDEX_DIR

def load_pdfs(path: str):
    docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    for pdf in glob.glob(os.path.join(path, "**", "*.pdf"), recursive=True):
        try:
            reader = PdfReader(pdf)
            text = "\n".join([p.extract_text() or "" for p in reader.pages])
            for chunk in splitter.split_text(text):
                docs.append(Document(page_content=chunk, metadata={"source": os.path.basename(pdf)}))
        except Exception as e:
            print("[WARN] failed to parse", pdf, e)
    return docs

def ingest(pdf_dir: str, index_dir: str = INDEX_DIR):
    ltm = LongTermMemory(index_dir=index_dir)
    docs = load_pdfs(pdf_dir)
    if not docs:
        print("No documents found.")
        return
    if ltm.is_empty():
        ltm.create(docs)
        print(f"Created new FAISS index at {index_dir} with {len(docs)} chunks.")
    else:
        ltm.add(docs)
        print(f"Added {len(docs)} chunks to existing index at {index_dir}.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ingest", type=str, help="Path to directory of PDFs to index.")
    args = ap.parse_args()
    if args.ingest:
        ingest(args.ingest)
    else:
        ap.print_help()
