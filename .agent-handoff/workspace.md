# Workspace
- Requirements: KERNEL_FORGE_SPEC.md; current operational state: WORKSTATE.md.
- Custom MCP service: method-bank/src/kernel_forge_method_bank/{server.py,db.py,models.py,schema.sql}.
- Tests: method-bank/tests/test_method_bank.py; run Conda base with -X utf8 -m unittest discover -s method-bank/tests -v.
- Python: <conda-base-python> (existing base).
- Integration commands: docs/TOOLING.md; live configuration: .codex/config.toml.
- Durable runtime data: data/method-bank.sqlite3 and data/papers/. These are ignored; preserve them for same-workspace handoff.
- Reproducible checks: scripts/probe_mcp.py and scripts/acceptance_methods.py.
- Evidence: docs/acceptance/; paper notes: docs/papers/.
- Entry docs: AGENTS.md and AGENT_HANDOFF.md. Supporting handoff files carry history/risks/decisions, not duplicate current state.
