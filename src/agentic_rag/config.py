import os
from dotenv import load_dotenv
load_dotenv()

DATA_DIR  = os.getenv("DATA_DIR", "./data/pdfs")
INDEX_DIR = os.getenv("INDEX_DIR", "./storage/faiss_index")
MEMORY_DB = os.getenv("MEMORY_DB", "./storage/memory.sqlite")

# Search
GOOGLE_CSE_ID   = os.getenv("GOOGLE_CSE_ID")        # CX id
GOOGLE_API_KEY  = os.getenv("GOOGLE_API_KEY")

# Models
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
HF_TOKEN        = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# GCP
GCP_PROJECT = os.getenv("GCP_PROJECT")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# MCP
USE_MCP = os.getenv("USE_MCP", "false").lower() in ["1", "true", "yes"]

