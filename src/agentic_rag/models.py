from __future__ import annotations
import os

class LLM:
    """
    Simple abstraction: if no API key is present, returns a deterministic mock
    so you can develop the rest of the stack offline.
    """
    def __init__(self):
        if os.getenv("OPENAI_API_KEY"):
            self.provider = "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            self.provider = "anthropic"
        elif os.getenv("HUGGINGFACEHUB_API_TOKEN"):
            self.provider = "huggingface"
        else:
            self.provider = "mock"

    def generate(self, prompt: str, system: str | None = None) -> str:
        if self.provider == "mock":
            return f"[MOCK-LLM] {prompt[:400]} ..."
        # Example OpenAI via LangChain (optional):
        if self.provider == "openai":
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
            template = ChatPromptTemplate.from_messages([
                ("system", system or "You are a helpful AI."),
                ("human", "{input}")
            ])
            chain = template | llm | (lambda x: x.content)
            return chain.invoke({"input": prompt})
        return "[LLM-NOT-CONFIGURED]"
