# First Learner-Kernel research cycle

Status: source-grounded preparation completed after Kernel-Forge acceptance. Learner-Kernel product requirements are the next input.

## Work performed using Forge

Recovered state through the handoff entry points, queried the Method Bank compactly, retrieved exact papers through PaperPipe and its cited MCP, and stored independently derived candidate methods. The no-history execution and provenance chain are in [acceptance/end-to-end.md](acceptance/end-to-end.md).

| Situation | Retrieved method | Evidence-backed next action |
|---|---|---|
| Delegate a bounded implementation task | METHOD-MINIMUM-SUFFICIENT-CONTEXT (reviewed, universal) | Supply goal, artifact pointers, constraints, acceptance checks and expected output; inspect sufficiency after completion. |
| Resume this repository | METHOD-VERIFY-HANDOFF (candidate, project) | Read WORKSTATE and validate the next relevant claim against files/tests. |
| Attention gradients weaken as key dimension grows | METHOD-SCALE-BEFORE-SOFTMAX (candidate, domain) | Measure logits and gradients; compare scaling under a fixed workload. Source: Attention Is All You Need, section 3.2.1, equation (1). |
| Execution requires singleton or tiny batches | METHOD-MATCH-NORMALIZATION-STATISTICS-TO-EXECUTION (candidate, domain) | Include per-example normalization in a controlled comparison and test dependence on co-batched examples. Source: Layer Normalization, section 3, equation (3). |

The first method has two successful bounded-context recovery experiments documented in the acceptance reports; its database review links the initial experiment. Paper-derived abstractions remain candidates until workload evidence supports review.

## Selected conditional experiment

If the product requires singleton execution, compare no normalization, batch normalization and layer normalization at batch sizes 1, 4 and a representative larger baseline, with equal training budgets. Record held-out task quality, latency and memory. At fixed weights vary other examples in the batch, verify the reduction axis, and specify epsilon/zero-variance handling. Batch-normalization inference using fixed running statistics can also be batch-independent, so the perturbation check alone does not select a winner.

If attention is part of the actual product, separately inspect dimension-dependent logit scaling before changing its optimizer. Preserve each source's assumptions and track measured results before changing candidate status.

## Exact next step

Create `LEARNER_KERNEL_SPEC.md` from the product owner's requirements, covering the learning task, inputs/outputs, update and persistence semantics, execution constraints, evaluation data/metrics, and acceptance thresholds. Then use `method_search` on those concrete situations and draft the smallest implementation task packet. The current repository contains the Forge specification; it does not yet define those Learner-Kernel product requirements.
