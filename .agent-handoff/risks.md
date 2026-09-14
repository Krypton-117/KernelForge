# Risks, Blockers, And Unknowns
- No known blocker for Kernel-Forge acceptance. PaperQA's observed late-import timeout is mitigated by the verified startup shim; keep using the configured launcher.
- Context7 mixes versioned and main-branch snippets; inspect source URLs before relying on version-specific behavior.
- Sparse retrieval is keyword-based; generated synthesis and dense embeddings are not configured.
- Runtime data is ignored: preserve data/ locally; new clones require re-ingestion/indexing per docs/TOOLING.md.
- Host sandbox process/file helpers failed before execution; approved unsandboxed commands work.
- Learner-Kernel product scope is UNKNOWN here; a research brief can prepare evidence, but implementation needs its own specification.
