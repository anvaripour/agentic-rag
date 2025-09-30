import json, subprocess, sys, os
from typing import Dict, Any, Optional

class MCPClient:
    """
    Minimal MCP client that spawns a server process and communicates via stdio.
    Assumes JSON-RPC 2.0 protocol. Extend for WebSockets if needed.
    """
    def __init__(self, server_cmd: list[str]):
        self.proc = subprocess.Popen(
            server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self._id = 0

    def request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self._id += 1
        req = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params}
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()

        # Read one line of JSON back
        assert self.proc.stdout is not None
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("No response from MCP server")
        resp = json.loads(line.strip())
        return resp.get("result", resp)

    def close(self):
        if self.proc:
            self.proc.terminate()
