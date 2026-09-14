"""Local MCP stdio server. Stdout contains only newline-delimited JSON-RPC."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys
from db import MethodBank
from models import DESCRIPTIONS, SCHEMAS

class ProtocolError(Exception):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)

class Server:
    def __init__(self, bank):
        self.bank = bank
        self.initialized = False
        self.ready = False

    def handle(self, request):
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
            raise ProtocolError(-32600, "Invalid JSON-RPC request")
        if "id" in request and (isinstance(request["id"], bool) or not isinstance(request["id"], (str, int))):
            raise ProtocolError(-32600, "Request id must be a string or integer")
        name, params = request["method"], request.get("params", {})
        if "id" not in request:
            if name == "notifications/initialized" and self.initialized:
                self.ready = True
            return None
        if not isinstance(params, dict):
            raise ProtocolError(-32602, "params must be an object")
        if name == "ping":
            result = {}
        elif name == "initialize":
            if self.initialized:
                raise ProtocolError(-32600, "Already initialized")
            if not isinstance(params.get("protocolVersion"), str) or not isinstance(params.get("capabilities"), dict) or not isinstance(params.get("clientInfo"), dict):
                raise ProtocolError(-32602, "protocolVersion, capabilities and clientInfo are required")
            supported = ("2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25")
            version = params["protocolVersion"]
            self.initialized = True
            result = {"protocolVersion": version if version in supported else supported[-1],
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "kernel-forge-method-bank", "version": "0.1.0"},
                "instructions": "Search compact methods first, then fetch selected methods. Retrieve sources only when verification is needed. Keep source claims separate from interpretations and generalized principles. New methods are candidates until explicitly reviewed."}
        elif not self.ready:
            raise ProtocolError(-32000, "Initialize and send notifications/initialized first")
        elif name == "tools/list":
            if params.get("cursor"):
                raise ProtocolError(-32602, "No pagination cursor is supported")
            result = {"tools": [{"name": tool, "description": DESCRIPTIONS[tool], "inputSchema": schema,
                "annotations": {"readOnlyHint": tool not in ("method_add_candidate", "method_review"),
                "destructiveHint": False, "openWorldHint": False}} for tool, schema in SCHEMAS.items()]}
        elif name == "tools/call":
            tool = params.get("name")
            if not isinstance(tool, str) or tool not in SCHEMAS:
                raise ProtocolError(-32602, "Unknown tool")
            try:
                data = self.bank.call(tool, params.get("arguments", {}))
                result = {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, allow_nan=False)}], "isError": False}
            except (ValueError, sqlite3.Error) as error:
                result = {"content": [{"type": "text", "text": str(error)}], "isError": True}
        else:
            raise ProtocolError(-32601, "Method not found")
        return {"jsonrpc": "2.0", "id": request["id"], "result": result}

def reject_constant(value):
    raise ValueError(f"Non-finite JSON: {value}")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(__file__).resolve().parents[3] / "data" / "method-bank.sqlite3"
    parser.add_argument("--db", default=os.environ.get("KERNEL_FORGE_DB", str(default)))
    args = parser.parse_args()
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    bank = MethodBank(args.db)
    server = Server(bank)
    try:
        for line in sys.stdin:
            request = None
            try:
                request = json.loads(line, parse_constant=reject_constant)
                response = server.handle(request)
            except (json.JSONDecodeError, ValueError):
                response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
            except ProtocolError as error:
                request_id = request.get("id") if isinstance(request, dict) else None
                if isinstance(request_id, bool) or not isinstance(request_id, (int, str)):
                    request_id = None
                response = {"jsonrpc": "2.0", "id": request_id, "error": {"code": error.code, "message": str(error)}}
            if response is not None:
                print(json.dumps(response, ensure_ascii=False, allow_nan=False), flush=True)
    finally:
        bank.close()

if __name__ == "__main__":
    main()
