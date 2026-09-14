# Attention: first numerical-stability research note

Project: Kernel-Forge / prospective Learner-Kernel research. This is evidence preparation, not a claim that Learner-Kernel has an attention architecture.

## Source and claim

Vaswani et al., Attention Is All You Need, arXiv:1706.03762, section 3.2.1, equation (1). PaperPipe library name: attention. Exact local source: data/papers/papers/attention/source.tex, lines 536-553. The source digest is recorded in docs/acceptance/method-provenance.json.

The authors suspect that larger dot products can push softmax into a region with weak gradients. Their attention divides logits by sqrt(d_k). The footnote's variance argument assumes independent, zero-mean, unit-variance components.

Canonical snippet: “extremely small gradients” (paper: attention; arXiv:1706.03762; source: tex; ref: section 3.2.1).

## Method sketch

Attention(Q,K,V) = softmax(Q K^T / sqrt(d_k)) V.

Source claim: this is the paper's scale correction.
Interpretation: when instability increases with key dimension, measure logit scale before changing the optimizer.
Generalized candidate: investigate dimension-dependent aggregate variance before selecting a normalization factor.

## Evaluation

This note does not reproduce the paper's training experiments or establish improved Learner-Kernel performance. The proposed engineering check holds the workload fixed, varies key dimension, and compares logit variance, saturation and gradient statistics with/without scaling. Benchmark numbers are not needed for this narrow extraction.

## Limits

The variance argument relies on assumptions that learned representations may violate. Generalizing beyond dot-product attention is an inference requiring validation. The method remains candidate, not reviewed.

## Implementation checklist

- Recover the actual Learner-Kernel specification before choosing an architecture.
- Retrieve METHOD-SCALE-BEFORE-SOFTMAX through Method Bank if the workload has attention instability.
- Follow provenance to the exact formula and assumptions.
- Measure the workload; record the decision and evidence before promoting a candidate.
