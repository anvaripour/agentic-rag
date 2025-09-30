#!/usr/bin/env python
import sys, json
from ...agents.cloud_agent import CloudAgent

ca = CloudAgent()

def handle(req):
    method = req.get("method")
    params = req.get("params", {})
    if method == "call":
        instr = params.get("instruction")
        return {"results": ca.call(instr)}
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
