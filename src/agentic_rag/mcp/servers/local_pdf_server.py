#!/usr/bin/env python
import sys, json
from ...memory import LongTermMemory
from ...config import INDEX_DIR

ltm = LongTermMemory(INDEX_DIR)

def handle(req):
    method = req.get("method")
    params = req.get("params", {})
    if method == "search":
        q = params.get("query")
        k = params.get("k", 5)
        return {"results": ltm.search(q, k)}
    return {"error": f"Unknown method {method}"}

def main():
    for line in sys.stdin:
        try:
            req = json.loads(line.strip())
            resp = {"jsonrpc": "2.0", "id": req.get("id"), "result": handle(req)}
        except Exception as e:
            resp = {"jsonrpc": "2.0", "error": str(e)}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
