# Decisions
- 2026-09-13: Keep WORKSTATE.md authoritative to meet spec section 14; handoff index/snapshot route to it and evidence files carry detail.
- 2026-09-13: User requires Conda base. Use verified absolute interpreter path.
- 2026-09-13: Version-control continuity artifacts so fresh agents can recover without chat history (spec C).
- 2026-09-13: Use upstream PaperQA sparse local embeddings to satisfy cited retrieval without model credentials. Two-paper indexed retrieval passed.
- 2026-09-13: Preload PaperQA before FastMCP threads. Direct retrieval passed while late imports timed out; scripts/paperqa_server.py passed the actual configured MCP probe without altering upstream packages.
- 2026-09-13: First Learner-Kernel cycle selected conditional measurement experiments using retrieved candidates. Architecture selection waits for product requirements; see docs/LEARNER_KERNEL_FIRST_CYCLE.md and final acceptance report.
