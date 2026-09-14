# Fresh-agent end-to-end acceptance

Status: **PASS**, specification section 23. Executed by a no-history delegated Codex agent using repository files rather than parent conversation. Recorded 2026-09-13 Asia/Shanghai; machine event time is 2026-09-12T20:30:34Z.

## Recovery and minimum sufficient context

Recovered in order: AGENTS.md, WORKSTATE.md, AGENT_HANDOFF.md, then snapshot, risks and backlog. The packet correctly identified final acceptance as pending, Conda base and UTF-8 as required, the configured PaperQA startup shim, ignored runtime-data preservation, and unknown Learner-Kernel architecture. Then read spec section 23, docs/TOOLING.md, docs/METHOD_SCHEMA.md, the client scripts, relevant Method Bank models/database code and configured MCP entries. Nine unittest smoke tests passed in 1.466 seconds. Git showed the implementation/docs untracked; no claim of an existing release commit was made.

This bounded packet was sufficient to select and execute the next task. No work-log, archive, parent conversation, or full historical validation log was needed. This is an observed single-agent recovery success, not proof that the packet is globally minimal or sufficient for every future task. A full LaTeX print was initially oversized/truncated; focused source search and lines 117-130 recovered the exact evidence. The instruction packet itself remained small; task-local evidence was loaded on demand.

## Source retrieval and independent extraction

Read cached upstream PaperPipe README MCP/CLI guidance, upstream PaperQA sparse-embedding guidance, and SDK v1.x client documentation before tool use (source URLs in docs/TOOLING.md). Applied papi/papi-ground. Retrieved exact LaTeX using `scripts/papi.py show layer-normalization --level tex`. Retrieved cited evidence through the actual `.codex/config.toml` paperqa entry, official MCP ClientSession, and upstream `retrieve_chunks` with query `layer normalization different training cases mini-batch size online regime`, k=5. The local sparse index had no failed files. Rank 2 returned `layer-normalization pages 2-3`, citation `Jimmy Lei Ba et al. (2016). Layer Normalization.` Raw chunks are in ignored `end-to-end-retrieval.log`; regeneration is below.

Short source quote: “different training cases have different normalization terms” (paper: layer-normalization, arXiv: 1607.06450, source: tex, ref: section 3, equation 3).

Equation (3) computes mu as the mean of a_i over H hidden units and sigma as the square root of the mean squared deviation from that mu. H is the number of hidden units; the reduction is within each individual example. Exact locator: `data/papers/papers/layer-normalization/source.tex` lines 117-130; equation label `eq:ln`; equation body lines 124-126. Line 130 explicitly permits batch size one.

| Evidence | SHA-256 |
|---|---|
| source.tex | d578147641107765ce95ba50aedeaae6ea6623a4aa54ae4eabc35e9129fb09d4 |
| paper.pdf | c464f839fb8d59f7fde92f9b4caa67c2d1f2f196b88f93fb60502249df0aaef7 |
| cited chunk text, UTF-8 | 818522f927eca49db0a01ae1ed3b4a072e61821241c52a548001df18d3e70684 |

The independently derived method separates:

- **Source claim:** Layer Normalization calculates within-case hidden-unit statistics and permits online batch size one.
- **Interpretation:** For individual-example or tiny-batch operation, evaluate this normalization and test that other examples cannot change its result at fixed weights.
- **Generalization:** Choose the population supplying statistics to match the independence and information available during execution. This abstraction is agent-derived, not an assertion that the paper proves it universally.

## Durable MCP chain

Added new candidate `METHOD-MATCH-NORMALIZATION-STATISTICS-TO-EXECUTION` with independent source `SOURCE-LAYER-NORMALIZATION-1607-06450` using `method_add_candidate`. Source URI: https://arxiv.org/abs/1607.06450. Status remains candidate, with no review approval invented.

Closed the initial Method Bank stdio process, opened a fresh process/ClientSession from the actual project config, searched normalization with domain scope, execution-contract tag and candidate status, and retrieved the full method. The restored record equals the original. Search remains compact. `source_get` returns the independent source plus a link back to this method and its locator. Re-reading the source path from returned metadata reproduces its stored SHA-256. `end-to-end-candidate.json` contains the insertion payload; `end-to-end-first-run.json` preserves the first successful add. `end-to-end-evidence.json` records the latest successful replay, full method/source round trip, hashes and short retrieval metadata.

## Engineering decision informed

Decision made for the next research cycle: include a per-example normalization arm in a controlled small-batch experiment if Learner-Kernel's eventual workload requires individual-example execution. Specify batch sizes 1, 4 and a larger baseline; compare no normalization, batch normalization and layer normalization under equal training budgets. At fixed weights, vary co-batched examples and check the normalization operation's outputs; record held-out task quality, latency and memory. Confirm the normalized axis and explicitly choose/test epsilon for zero variance, which equation (3) does not specify.

This selects an evidence-backed experiment and its acceptance measurements, not a production architecture. No model training or quality/speed improvement was claimed. Batch-normalization inference with fixed running statistics is also batch-independent; the perturbation test alone does not establish superiority. The paper's preliminary convolutional results in the Convolutional Networks subsection favor batch normalization, so no universal replacement is justified.

## Reproduction

Run from the repository root with the existing data directory and installed tooling:

```powershell
$py = '<conda-base-python>'
& $py -X utf8 -m unittest discover -s method-bank/tests -v
& $py -X utf8 docs/acceptance/retrieve_layer_norm.py
& $py -X utf8 docs/acceptance/acceptance_layer_norm.py
```

The first script starts the configured upstream MCP and regenerates ignored raw evidence. The second checks the cited passage and LaTeX anchor, writes/validates the exact payload through MCP, opens a new Method Bank process, and validates retrieval/provenance. Re-runs accept the same existing candidate only if payload and provenance are unchanged; `added_new_candidate_this_run` then becomes false. The original new-add evidence is preserved in `end-to-end-first-run.json`. The parent also replayed the test after making the existing-ID lookup independent of search pagination. A new clone must re-ingest/index papers per docs/TOOLING.md; changed upstream bytes require rechecking locators/hashes rather than claiming identical source evidence.

## Limitations and closeout

Sandbox shell creation failed before execution; escalated shell calls worked. Sparse retrieval is keyword-based and raw-citation retrieval, not LLM synthesis or dense semantic retrieval. Tests verify Forge integration and persistence, not scientific efficacy. Runtime corpus/database remain ignored and must be preserved separately. WORKSTATE was updated with this result and an exact remaining closeout step. Parent owns supporting handoff updates, maintenance and release checkpoint.

**Cited papers**: Layer Normalization, arXiv:1607.06450.
