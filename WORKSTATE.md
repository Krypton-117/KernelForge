# Mission
Deliver Kernel-Forge v0.1 per KERNEL_FORGE_SPEC.md, then prepare the first Learner-Kernel research cycle.
# Current Objective
Kernel-Forge v0.1 is complete and verified. Resume by defining Learner-Kernel requirements using the completed first research cycle.
# Active Work
No Kernel-Forge implementation is in progress. First research-cycle evidence and conditional experiment selection are in docs/LEARNER_KERNEL_FIRST_CYCLE.md.
# Verified Completed Work
- README Contributors credits Krypton-117 for concept/direction and OpenAI Codex as AI coding assistant for implementation, testing and documentation. Documentation-only change; checked diff and remote publication after push.
- Installed personal agent-handoff from WeirdSky924/agent-handoff-skill; initialized and maintained repository continuity.
- Conda base Python 3.12.9: <conda-base-python>.
- Six-tool Method Bank: validated atomic writes, SQLite/FTS5 filters, many-to-many provenance, review history and reviewed universal seed.
- Nine local regression/stdio tests passed; official MCP SDK interoperability passed.
- Acceptance A/B passed via scripts/acceptance_methods.py: paper-to-method provenance, compact three-scope search and process-restart persistence.
- Initial fresh no-history subagent passed C/D; universal seed review links docs/acceptance/continuity-initial.md.
- PaperPipe 1.11.0 installed through base user site; seven upstream skills installed. Identifier, URL, title and local-PDF paths verified.
- Attention Is All You Need and Layer Normalization stored with PDFs/LaTeX; project attention note readable via PaperPipe.
- PaperQA local sparse index contains two papers with zero failures; actual configured MCP returned cited passages from both papers and the softmax-gradient passage.
- Context7 live query returned explicit Python v3.11.14 source URLs. pip check passed.
- Final no-history section 23 passed: Layer Normalization cited MCP retrieval, new candidate METHOD-MATCH-NORMALIZATION-STATISTICS-TO-EXECUTION, fresh-process retrieval and source_get hash validation; nine smoke tests passed. See docs/acceptance/end-to-end.md.
# Pending Work
Kernel-Forge v0.1: none. Next product step: define LEARNER_KERNEL_SPEC.md from the product owner's requirements before implementing Learner-Kernel.
# Current Decisions
- Use user's Conda base, UTF-8, and process-local CLI paths; no new environment.
- WORKSTATE owns operational state; handoff index/snapshot route to it and evidence files hold detail.
- SQLite/FTS5 service is standard-library-only. PaperQA/Context7 remain upstream integrations.
- Sparse PaperQA retrieval is local keyword retrieval, not dense semantic embeddings or LLM synthesis.
- scripts/paperqa_server.py preloads PaperQA before upstream MCP startup: late imports inside requests timed out on this Windows runtime; preload probe passed.
- Keep continuity/evidence in Git; keep runtime data ignored but preserve data/ for this workspace.
# Evidence and Artifacts
README.md; docs/METHOD_SCHEMA.md; docs/TOOLING.md; docs/acceptance/{unit-tests.txt,method-bank-mcp.json,method-provenance.json,paperpipe-mcp.json,context7-mcp.json,continuity-initial.md,pip-check.txt}; docs/papers/attention-note.md; docs/LEARNER_KERNEL_FIRST_CYCLE.md; docs/acceptance/{end-to-end.md,end-to-end-evidence.json,end-to-end-candidate.json,retrieve_layer_norm.py,acceptance_layer_norm.py}.
# Verification Status
A/B and initial C/D passed. All configured MCP probes passed. Final fresh-agent section 23 passed; full provenance and bounded-context assessment are in docs/acceptance/end-to-end.md. Parent replay and final SQLite integrity/foreign-key/source-hash checks passed (4 methods, 3 sources). Candidate scientific efficacy is not validated.
# Repository State
Implementation checkpoint ea789b0 is committed locally; final handoff is tracked in a follow-up commit (inspect git log -1). Original specification preserved. data/ retains the durable corpus/database and is ignored by Git; tests use temporary databases. Published sanitized main to https://github.com/Krypton-117/KernelForge. Verified remote commit 74cb64f matched local HEAD, GitHub README API returned 2970 bytes, and remote tree contained 48 files without paper originals or databases. Earlier local history remains on master: do not push master or use --all. MCP config contains portable placeholders requiring local substitution.
# Resume From Here
Read docs/LEARNER_KERNEL_FIRST_CYCLE.md, then create LEARNER_KERNEL_SPEC.md from the product owner's learning task, interfaces, update/persistence semantics, execution constraints and measurable acceptance thresholds. Retrieve relevant methods against those concrete situations before planning implementation. To verify this Forge checkpoint first, run the Conda base command `python -X utf8 -m unittest discover -s method-bank/tests -v`; integration replay commands are in docs/acceptance/README.md.
# Last Updated
2026-09-14 (Asia/Shanghai; live evidence timestamps use UTC)
