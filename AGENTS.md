# Kernel-Forge
Development support for Learner-Kernel: source grounding, Method Bank, durable continuity.

1. Read `WORKSTATE.md`, then `AGENT_HANDOFF.md` and its recovery pointers.
2. Inspect Git state and the relevant `method-bank/` code; verify state claims with smoke tests before resuming.
3. Read upstream documentation before configuring or using external tools; sources and access are in `docs/TOOLING.md`.

Use Conda base: `<conda-base-python>` (Python 3.12.9). Use `-X utf8`.
- Tests: `python -X utf8 -m unittest discover -s method-bank/tests -v`.
- Method Bank: `python -X utf8 method-bank/src/kernel_forge_method_bank/server.py` (MCP JSON lines); database `data/method-bank.sqlite3`.
- PaperPipe: `python -X utf8 scripts/papi.py <command>`; local corpus `data/papers/`.
- Context7 and upstream PaperQA MCP: project `.codex/config.toml`; probes in `scripts/probe_mcp.py`.
- API: `docs/METHOD_SCHEMA.md`; acceptance artifacts: `docs/acceptance/`.

<!-- AGENT_HANDOFF_PROTOCOL:START -->
## Continuity protocol
`WORKSTATE.md` owns current operational state using the specification's fixed headings.
`AGENT_HANDOFF.md` routes to `.agent-handoff/snapshot.md`, `risks.md`, `backlog.md`; read validation/decisions only as needed.
At verified checkpoints and before closeout, update WORKSTATE and the smallest relevant supporting evidence files. Replace stale state; retain evidence paths and an exact next executable step.
Verify source/code facts rather than treating handoff prose as proof. Read bounded sections, re-anchor uncertain reads with search, and preserve unrelated changes.
Use installed `agent-handoff/scripts/maintain_handoff.py --repo . --compact-if-needed` after updates. Keep the snapshot below 240 lines; inspect the skill's quality guide when repairing or rotating history.
A continuation request resumes from WORKSTATE without relying on chat history.
<!-- AGENT_HANDOFF_PROTOCOL:END -->
