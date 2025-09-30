# Agentic RAG

An **Agentic Retrieval-Augmented Generation (RAG)** system with:  

- **Reasoning:**  
  - *Chain-of-Thought (CoT)* for concise outlines  
  - *ReAct* for tool-use planning  

- **Memory:**  
  - *Short-Term Memory (STM)*: rolling dialogue context (SQLite)  
  - *Long-Term Memory (LTM)*: FAISS index over local PDFs (Vision–Language Models research)  

- **Agents & Tools:**  
  - *Local Data Agent* → PDF retrieval (FAISS)  
  - *Search Agent* → Google Custom Search (or MCP search server)  
  - *Cloud Agent* → GCP stub (easily extendable to Vertex AI / GCS / BigQuery)  

- **MCP Support:**  
  - Local PDF, Search, and Cloud tools can run as **MCP servers** (JSON-RPC stdio).  
  - Agents can call MCP clients instead of local Python functions.  

- **LangGraph Orchestration:**  
  - Multi-node graph execution for planner, tools, and answer synthesis.  
  - Conditional looping (tools execute only if the plan requires them).  
  - STM updates at every step (query, outline, tool results, final answer).  

---



