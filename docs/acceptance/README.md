# Kernel-Forge v0.1 acceptance evidence

Date: 2026-09-13 Asia/Shanghai. Machine/environment details: environment.json. Current release state is maintained in ../../WORKSTATE.md.

| Requirement | Evidence | Result |
|---|---|---|
| Durable personal skill and repository recovery | environment.json; continuity-initial.md; ../../AGENT_HANDOFF.md | Installed and initialized; capacity checks clean |
| Local Method Bank behavior | unit-tests.txt | 9 tests passed, including rollback, provenance, filtering, review and stdio |
| MCP interoperability | method-bank-mcp.json | Official SDK initialized actual configured server, discovered six tools and retrieved seed |
| A: paper-to-method provenance | method-provenance.json; example-methods.json | Passed; source hash/locator follows back to PaperPipe LaTeX |
| B: compact method retrieval across scopes | method-provenance.json | Passed; universal/domain/project, no full corpus in search result |
| C/D: fresh checkpoint recovery and bounded context | continuity-initial.md | Passed at initial checkpoint; experiment referenced in universal seed review |
| PaperPipe ingestion | attention and layer-normalization under local data/papers/ | Identifier and URL ingested; title resolved an existing paper; local PDF ingested in isolated data/local-pdf-probe/ |
| Exact source, equations and project notes | ../papers/attention-note.md; PaperPipe show/notes commands | Verified against original LaTeX, equation (1), section 3.2.1 |
| PaperPipe upstream MCP retrieval | paperpipe-mcp.json | Passed; local sparse index, two papers, zero failures, cited passage including gradients |
| Version-aware software docs | context7-mcp.json | Passed; requested advertised Python v3.11.14, verified explicit versioned source URLs |
| Environment dependencies | pip-check.txt | No broken requirements |

Final section 23 acceptance passed: [end-to-end.md](end-to-end.md). The new-add evidence is preserved in end-to-end-first-run.json; end-to-end-evidence.json records the successful parent replay. final-integrity.json verifies database integrity, foreign keys and both paper-source hashes. The first real research cycle is recorded in [../LEARNER_KERNEL_FIRST_CYCLE.md](../LEARNER_KERNEL_FIRST_CYCLE.md).

## Reproduction

From repository root using the documented Conda base interpreter:

```powershell
& $py -X utf8 -m unittest discover -s method-bank/tests -v
& $py -X utf8 scripts/probe_mcp.py method-bank
& $py -X utf8 scripts/probe_mcp.py paperpipe
& $py -X utf8 scripts/probe_mcp.py context7
& $py -X utf8 scripts/acceptance_methods.py
```

Set $py as shown in ../../README.md. The local corpus and indices must be present; a new clone follows the ingestion/index instructions in ../TOOLING.md. Context7 requires network. Test databases are temporary. Live probes check actual project config and overwrite their compact JSON evidence with passed or failed status.

## Observed failures resolved

- Initial prototype rejected MCP initialize. Replaced with the implemented lifecycle and six semantic tools.
- PaperPipe LaTeX writing used Windows GBK. Explicit UTF-8 fixed ingestion.
- User-site pqa CLI was not on PATH. The wrapper provides Scripts directories process-locally.
- PaperQA dependency imports during MCP tool requests stalled, despite identical direct retrieval succeeding. The startup shim preloads PaperQA before upstream MCP threads; strict configured retrieval then passed.

Raw setup/diagnostic logs remain local and ignored. Sparse embeddings provide local keyword retrieval, not model-generated synthesis. Context7 can mix main and version-specific results, so only explicit versioned URLs count. This delivery does not establish any Learner-Kernel model-performance result.
