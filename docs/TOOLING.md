# External tools and reproducible verification

Read the relevant upstream documentation before changing any setup. Credentials are not stored in this repository.

## Upstream evidence

| Tool | Documentation read |
|---|---|
| agent-handoff | https://github.com/WeirdSky924/agent-handoff-skill/blob/main/SKILL.md and README; installed references/codex-rules.md and quality.md |
| Codex MCP | https://developers.openai.com/codex/mcp |
| PaperPipe | https://github.com/hummat/paperpipe/blob/main/README.md; installed 1.11.0 CLI help and Codex skills |
| Context7 | https://github.com/upstash/context7/blob/master/README.md |
| MCP wire | https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle and /server/tools |
| MCP SDK v1 | https://github.com/modelcontextprotocol/python-sdk/blob/v1.x/docs/client.md |
| SQLite FTS5 | https://www.sqlite.org/fts5.html |
| Python sqlite3 | https://docs.python.org/3.12/library/sqlite3.html |
| PaperQA local sparse embedding | https://github.com/Future-House/paper-qa#embedding-model |
| pip | https://pip.pypa.io/en/stable/cli/pip_install/ |
| Conda | https://docs.conda.io/projects/conda/en/latest/commands/run.html |
| Git | https://git-scm.com/docs/git-status and https://git-scm.com/docs/git-init |

Upstream documents were fetched to ignored `docs/upstream/` for inspection. Retrieved Context7 documentation is transient implementation context; acceptance records retain source/version evidence, not operational instructions copied from returned snippets.

## Interpreter and installation

```powershell
$py = '<conda-base-python>'
& $py -m pip install -r requirements-tooling.txt
& $py -X utf8 -m paperpipe install skill --codex --copy
& $py -m pip check
```

This machine uses the existing Conda base (Python 3.12.9). Its installation folder is not writable; pip installed into the base interpreter's user site. No new Conda environment was created. Upstream installed seven PaperPipe skills into `~/.agents/skills`, its current Codex discovery location. agent-handoff is in `~/.codex/skills/agent-handoff`.

MCP SDK resolved to 1.30.0 (PaperPipe constrains MCP <2). Reading the SDK's main-branch docs alone would select v2, so client usage was checked against the v1.x documentation and installed source.

## PaperPipe

Always use the wrapper so the database is this repository's `data/papers/`, UTF-8 is enabled, and user-site CLI scripts can be found:

```powershell
& $py -X utf8 scripts/papi.py add 1706.03762 --name attention --tags kernel-forge --no-llm --no-tldr
& $py -X utf8 scripts/papi.py add https://arxiv.org/abs/1607.06450 --name layer-normalization --tags kernel-forge --no-llm --no-tldr
& $py -X utf8 scripts/papi.py show attention --level tex
& $py -X utf8 scripts/papi.py show attention --level eq
& $py -X utf8 scripts/papi.py notes attention --print
& $py -X utf8 scripts/papi.py index --backend search
& $py -X utf8 scripts/papi.py search 'attention'
& $py -X utf8 scripts/papi.py index --backend pqa --pqa-embedding sparse --pqa-verbosity 0
& $py -X utf8 scripts/probe_mcp.py paperpipe
```

All four input forms were verified: arXiv identifier, arXiv URL, title resolution (recognized the existing paper), and local PDF ingestion in a separate test library. The local PDF command is `add --pdf <local-file> --title <title> --no-llm`.

The local sparse mode is upstream-supported keyword retrieval, not semantic dense embeddings or generated cross-paper answers. It provides raw indexed passages with citations through PaperPipe's retrieve_chunks. Full `papi ask` synthesis or dense embeddings require a separately configured model backend; no such credential is needed for the v0.1 source-grounding path.

Windows discoveries: implicit GBK cannot encode all downloaded LaTeX; `-X utf8` fixes this. PaperPipe checks for `pqa` on PATH even when its package is installed; the wrapper supplies the relevant Scripts paths process-locally. LiteLLM's optional remote price-map fetch can delay a local cold start; its upstream module documents `LITELLM_LOCAL_MODEL_COST_MAP=True` for using the bundled map.

## Context7

Project config uses the upstream remote MCP endpoint `https://mcp.context7.com/mcp`. No Node installation is required. Anonymous requests worked during validation; higher-rate access can be configured separately if needed. `codex mcp list` showing “Not logged in” is not a failed anonymous retrieval.

```powershell
& $py -X utf8 scripts/probe_mcp.py context7
```

The live test resolves Python, then requests `/python/cpython/v3.11.14`, an advertised version. Verify each returned source URL: some results may be from main even in a versioned query. The v3.11.14 sqlite3 example was observed; it is not evidence of a Python 3.12-specific Context7 index. Python 3.12 behavior is verified by local tests and the official 3.12 docs.

## Codex registration

`.codex/config.toml` uses project scope (requires a trusted project) and absolute paths for this machine. On relocation, update those paths. It starts `scripts/paperqa_server.py` through Conda base; this preloads PaperQA before invoking the upstream paperqa_mcp main entry point. Direct upstream startup stalled while lazily importing dependencies inside a tool request; preloading fixed the observed Windows issue. The shim leaves upstream packages unchanged and forwards this machine's existing MKL_SERIAL=YES runtime setting. It leaves user-wide MCP configuration unchanged.

```powershell
codex mcp list
& $py -X utf8 scripts/probe_mcp.py method-bank
```

The official SDK probes verify live transport, discovery and tool calls. A separately recorded fresh-agent test verifies repository recovery; neither CLI listing nor a configuration file by itself proves successful retrieval.

## Recovery data

Keep `data/` with this working directory. A new clone must re-ingest the source papers, rebuild the sparse index and run `scripts/acceptance_methods.py`. The latter writes candidate examples from inspected source evidence and checks SHA-256 provenance. The checked-in `docs/acceptance/example-methods.json` records the original candidate payloads. If a future upstream download differs, verify its locator and hash rather than silently retaining stale evidence.

## Portable configuration

Replace `<conda-base-python>` and `<repository-root>` in `.codex/config.toml` with local paths before configured MCP probes. Historical integration results describe the original configured workspace. Keep machine-specific values local.
