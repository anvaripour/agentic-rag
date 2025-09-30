from __future__ import annotations
from typing import Any, Dict

class CloudAgent:
    """Stub GCP hook; extend with GCS/Vertex/BigQuery as needed."""
    def call(self, instruction: str) -> Dict[str, Any]:
        return {"ok": True, "engine": "gcp", "note": "stubbed call", "instruction": instruction}
