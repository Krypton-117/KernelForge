"""Explicit live MCP probes using the official v1 SDK. No credentials are printed."""
import argparse
import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

ROOT = Path(__file__).resolve().parents[1]

def payload(result):
    assert not result.isError, result.content
    if result.structuredContent is not None:
        return result.structuredContent
    return json.loads(result.content[0].text)

async def inspect(session, kind):
    init = await session.initialize()
    tools = await session.list_tools()
    output = {"status": "passed", "checked_at": datetime.now(timezone.utc).isoformat(),
              "server": init.serverInfo.model_dump(exclude_none=True), "protocol": init.protocolVersion,
              "tools": [t.name for t in tools.tools]}
    if kind == "method-bank":
        result = payload(await session.call_tool("method_search", {"query": "context", "status": "reviewed"}))
        assert any(m["id"] == "METHOD-MINIMUM-SUFFICIENT-CONTEXT" for m in result)
        output["seed_search"] = result
    elif kind == "paperpipe":
        output["indexes"] = payload(await session.call_tool("list_pqa_indexes", {}))
        result = payload(await session.call_tool("retrieve_chunks",
            {"query": "dot products softmax gradients", "k": 3}))
        assert result["ok"] and result["chunks"], result
        assert result["index_files"]["total"] >= 2 and result["index_files"]["failed"] == 0, result
        output["retrieval"] = {k: v for k, v in result.items() if k != "chunks"}
        output["retrieval"]["chunks"] = [{
            "chunk_name": c["chunk_name"], "docname": c["docname"], "citation": c["citation"],
            "text_sha256": hashlib.sha256(c["text"].encode()).hexdigest(),
            "preview": c["text"][:160]} for c in result["chunks"]]
        assert all(c["citation"] and c["chunk_name"] for c in result["chunks"])
        output["contains_gradient_passage"] = any("gradients" in c["text"] and "softmax" in c["text"] for c in result["chunks"])
        assert output["contains_gradient_passage"], "Relevant methodological passage was not returned"
    else:
        resolved = await session.call_tool("resolve-library-id",
            {"libraryName": "python", "query": "Python sqlite3 transaction commit rollback"})
        assert not resolved.isError
        resolution = "\n".join(c.text for c in resolved.content if c.type == "text")
        assert "v3.11.14" in resolution, "Requested version is not advertised"
        docs = await session.call_tool("query-docs", {"libraryId": "/python/cpython/v3.11.14",
            "query": "sqlite3 connection context manager commit rollback transactions"})
        assert not docs.isError
        text = "\n".join(c.text for c in docs.content if c.type == "text")
        sources = sorted(set(re.findall(r"https://[^\s]+", text)))
        versioned = [url for url in sources if "/v3.11.14/" in url]
        assert versioned, "No version-specific source returned"
        output.update(library_id="/python/cpython/v3.11.14", versioned_sources=versioned,
                      other_sources=[url for url in sources if url not in versioned],
                      response_sha256=hashlib.sha256(text.encode()).hexdigest())
    return output

async def main(kind):
    # Probe the actual project configuration, not a parallel handwritten setup.
    config = tomllib.loads((ROOT/".codex/config.toml").read_text(encoding="utf-8-sig"))["mcp_servers"]
    entry = config[{"method-bank": "method-bank", "paperpipe": "paperqa", "context7": "context7"}[kind]]
    if "url" in entry:
        async with streamable_http_client(entry["url"]) as (read, write, _):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=120)) as session:
                output = await inspect(session, kind)
    else:
        params = StdioServerParameters(command=entry["command"], args=entry.get("args", []),
            cwd=entry.get("cwd"), env=entry.get("env"))
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=120)) as session:
                output = await inspect(session, kind)
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["method-bank", "paperpipe", "context7"])
    kind = parser.parse_args().kind
    try:
        result = asyncio.run(main(kind))
    except Exception as error:
        result = {"status": "failed", "checked_at": datetime.now(timezone.utc).isoformat(),
                  "error_type": type(error).__name__, "error": str(error)}
        (ROOT/"docs/acceptance"/f"{kind}-mcp.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        raise
    (ROOT/"docs/acceptance"/f"{kind}-mcp.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
