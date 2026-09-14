"""Acceptance A/B through the official MCP client; idempotent persistent examples."""
import asyncio
import hashlib
import json
from pathlib import Path
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
MID = "METHOD-SCALE-BEFORE-SOFTMAX"

async def call(session, name, args):
    result = await session.call_tool(name, args)
    if result.isError:
        raise RuntimeError(result.content[0].text)
    return json.loads(result.content[0].text)

async def ensure(session, payload):
    mid = payload["method"]["id"]
    found = await session.call_tool("method_get", {"method_id": mid})
    if not found.isError:
        existing = json.loads(found.content[0].text)
        for key, value in payload["method"].items():
            assert existing[key] == value, f"Existing method differs: {mid}.{key}"
        assert existing["sources"] == payload["sources"], "Existing provenance differs"
        return
    await call(session, "method_add_candidate", payload)

async def main():
    paper = ROOT/"data/papers/papers/attention"
    source = paper/"source.tex"
    tex = source.read_text(encoding="utf-8")
    lines = tex.splitlines()
    line_no = next(i for i, line in enumerate(lines, 1) if "extremely small gradients" in line and not line.startswith("%"))
    assert "variance $d_k$" in lines[line_no-1]
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    paper_source = dict(source_id="SOURCE-ATTENTION-1706-03762", source_type="paper",
        title="Attention Is All You Need", external_id="arxiv:1706.03762",
        uri="https://arxiv.org/abs/1706.03762",
        metadata={"paperpipe_name": "attention", "source_path": str(source.relative_to(ROOT)).replace("\\", "/"),
                  "source_sha256": digest, "pdf_sha256": hashlib.sha256((paper/"paper.pdf").read_bytes()).hexdigest()},
        locator=f"section 3.2.1, equation (1), source.tex line {line_no}",
        relation="supports", note="Source statement is a proposed explanation under stated independence and variance assumptions.")
    domain = {"method": dict(id=MID, title="Scale aggregates before saturating nonlinearities",
        aphorism="Check scale before blaming the optimizer.",
        source_claim="The authors suspect larger dot products can saturate softmax and reduce gradients; they divide attention logits by the square root of key dimension.",
        interpretation="When attention gradients weaken as key dimension grows, inspect logit scale before changing optimization.",
        generalized_principle="Measure how aggregate variance changes with dimension before choosing a normalization factor.",
        trigger="Attention instability or softmax saturation when increasing key dimension.",
        scope_level="domain", scope_tags=["machine-learning", "numerical-stability"],
        action_bias="Inspect logit variance and gradient magnitude, then test scaling against a fixed baseline.",
        verification="Compare saturation and gradient statistics over multiple key dimensions; check that the source assumptions apply."),
        "sources": [paper_source]}
    project = {"method": dict(id="METHOD-VERIFY-HANDOFF", title="Verify a checkpoint before resuming",
        aphorism="A handoff points to evidence.",
        source_claim="The specification requires agents to verify relevant WORKSTATE claims against repository state before continuing.",
        interpretation="Recover through the short entry files, then run a bounded validation at the stated breakpoint.",
        generalized_principle="Treat written operational state as orientation and validate it before acting.",
        trigger="Resuming Kernel-Forge in a new session.", scope_level="project", scope_tags=["continuity"],
        action_bias="Read WORKSTATE and test the next relevant claim before changing code.",
        verification="A fresh agent identifies the objective, unfinished work and executable next step without conversation history."),
        "sources": [dict(source_id="SOURCE-KERNEL-FORGE-SPEC", source_type="repository",
            title="Kernel-Forge Specification v0.1", external_id="v0.1", uri="KERNEL_FORGE_SPEC.md",
            metadata={}, locator="sections 15, 21 and 22", relation="supports", note="Initial experiment: docs/acceptance/continuity-initial.md.")]}
    params = StdioServerParameters(command=sys.executable,
        args=["-X", "utf8", str(ROOT/"method-bank/src/kernel_forge_method_bank/server.py")], cwd=str(ROOT))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for payload in (domain, project):
                await ensure(session, payload)
            result = await call(session, "method_search", {"query": "softmax saturation", "scope_levels": ["domain"], "limit": 5})
            assert any(m["id"] == MID for m in result)
            assert all("sources" not in m and "source_claim" not in m for m in result)
            record = await call(session, "method_get", {"method_id": MID})
            provenance = await call(session, "source_get", {"source_id": paper_source["source_id"]})
            assert record["sources"][0]["metadata"]["source_sha256"] == digest
            assert any(link["method_id"] == MID for link in provenance["locators"])
            scopes = {m["scope_level"] for m in await call(session, "method_search", {})}
            assert {"universal", "domain", "project"} <= scopes
            seed = await call(session, "method_get", {"method_id": "METHOD-MINIMUM-SUFFICIENT-CONTEXT"})
            note = "Bounded no-history recovery passed C/D: docs/acceptance/continuity-initial.md. Context packet was sufficient; unrelated history was not needed."
            if not any(review["review_note"] == note for review in seed["reviews"]):
                await call(session, "method_review", {"method_id": seed["id"], "decision": "reviewed", "review_note": note})
    # Re-open the process to verify durable retrieval rather than a single-session cache.
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            restored = await call(session, "method_get", {"method_id": MID})
            assert restored == record
    evidence = {"acceptance_A": "passed", "acceptance_B": "passed", "method_id": MID,
        "source_id": paper_source["source_id"], "locator": paper_source["locator"],
        "source_sha256": digest, "scopes": sorted(scopes), "compact_search": result,
        "restart_verified": True, "engineering_decision": "For a key-dimension-dependent attention instability, measure logits and gradients before changing the optimizer; candidate requires workload verification."}
    (ROOT/"docs/acceptance/method-provenance.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    (ROOT/"docs/acceptance/example-methods.json").write_text(json.dumps([domain, project], indent=2), encoding="utf-8")
    print(json.dumps(evidence))

if __name__ == "__main__":
    asyncio.run(main())
