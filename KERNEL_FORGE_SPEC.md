# Kernel-Forge Specification v0.1

## 1. Purpose

Kernel-Forge is the development support layer used to build Learner-Kernel.

Its responsibility is to provide an engineering agent with three durable capabilities:

1. grounded access to research papers and technical sources;
2. structured storage and retrieval of reusable methodologies;
3. deterministic project continuity across independent agent sessions.

The Forge should remain small enough that its behavior is easy to inspect and verify.

---

# 2. Core Principle

Use **Minimum Sufficient Context**.

For every agent or subagent task, provide the smallest set of information sufficient to complete the assigned work reliably.

A task packet should be derived from:

- goal;
- required source material;
- relevant constraints;
- acceptance criteria;
- expected output.

Context selection is part of the engineering process.

---

# 3. System Layout

```text
Kernel-Forge
│
├── Source Grounding
│     ├── PaperPipe
│     └── Context7
│
├── Method Bank
│     └── local MCP server
│           └── SQLite + FTS5
│
└── Continuity
      ├── AGENTS.md
      └── WORKSTATE.md
```

The three areas have independent responsibilities.

---

# 4. Source Grounding

## 4.1 Scientific papers

Use PaperPipe as the paper-ingestion and paper-retrieval layer.

The Forge should configure PaperPipe for Codex and verify that Codex can:

- add a paper by identifier, URL, title or local PDF;
- retrieve exact paper content;
- inspect equations and source text when available;
- retrieve relevant passages with source attribution;
- create project-specific paper notes;
- query across papers.

Prefer source-grounded retrieval when extracting methodologies.

A methodology derived from a paper must preserve a pointer back to its supporting source.

---

## 4.2 Software documentation

Use Context7 as the version-aware software documentation source available to Codex.

It should be callable when implementation depends on external libraries or APIs.

Examples include:

- PocketFlow;
- MCP SDKs;
- database libraries;
- model SDKs;
- testing frameworks.

Retrieved documentation is implementation context, not persistent project state.

---

# 5. Method Bank

The Method Bank is the only custom persistent service required by Kernel-Forge v0.1.

Implement it as a local MCP server backed by SQLite.

Use SQLite FTS5 for initial retrieval.

The database is the source of truth.

---

# 6. Methodology Object

A methodology is a reusable way of approaching a class of problems.

It is distinct from a paper, historical episode, project fact or executable implementation.

Each methodology record must contain the following semantic fields.

```yaml
id: METHOD-...

title:

aphorism:

source_claim:

interpretation:

generalized_principle:

trigger:

scope_level:

scope_tags:

action_bias:

verification:

status:

created_at:

updated_at:
```

## `aphorism`

A concise human/LLM-readable formulation when one exists.

Example:

> Evidence before assertion.

---

## `source_claim`

What the cited source itself supports.

This field should remain close to the source.

---

## `interpretation`

What the researcher or agent infers from the source for the present problem.

---

## `generalized_principle`

A reusable methodological abstraction derived from the interpretation.

---

## `trigger`

The kind of situation in which the methodology becomes relevant.

---

## `scope_level`

One of:

```text
universal
domain
project
task
```

---

## `scope_tags`

Searchable domain and context labels.

Examples:

```text
research
search
software-engineering
agent-orchestration
experimental-design
```

---

## `action_bias`

How this methodology should influence a future decision.

It describes a decision tendency rather than a complete workflow.

---

## `verification`

How an agent can determine whether application of the methodology helped.

---

## `status`

Kernel-Forge v0.1 uses:

```text
candidate
reviewed
```

`candidate` means extracted but not yet accepted for routine use.

`reviewed` means explicitly reviewed for retrieval by engineering agents.

---

# 7. Provenance Model

Sources are independent database objects.

Minimum source schema:

```yaml
source_id:
source_type:
title:
external_id:
uri:
metadata:
```

Supported source types initially include:

```text
paper
documentation
human
agent
experiment
repository
```

Methods and sources have a many-to-many relation.

Each relation records:

```yaml
method_id:
source_id:
locator:
relation:
note:
```

`locator` should identify the smallest useful supporting location available, such as:

- page;
- section;
- equation;
- PaperPipe chunk;
- repository file and line range.

`relation` describes the role of the source, for example:

```text
supports
motivates
limits
contradicts
origin
```

---

# 8. Method Bank MCP Surface

Expose a small semantic API.

## `method_search`

Inputs:

```yaml
query:
scope_levels:
scope_tags:
status:
limit:
```

Returns compact candidate records.

Search title, aphorism, trigger, interpretation and generalized principle using FTS5.

---

## `method_get`

Input:

```yaml
method_id:
```

Returns the complete methodology record and provenance links.

---

## `method_add_candidate`

Accepts a complete candidate Methodology object and its provenance.

Writes atomically.

---

## `method_review`

Inputs:

```yaml
method_id:
decision:
review_note:
```

Records the review and updates its status.

---

## `method_sources`

Input:

```yaml
method_id:
```

Returns the supporting source records and locators.

---

## `source_get`

Input:

```yaml
source_id:
```

Returns source metadata and locators.

---

# 9. Retrieval Discipline

Method retrieval should follow:

```text
Task
↓
Situation description
↓
Method search
↓
Compact candidate list
↓
Method get for selected candidates
↓
Source retrieval only when verification is required
```

The initial search result should be compact.

Full source material is retrieved only when the current task needs it.

---

# 10. Paper-to-Method Distillation

When an agent studies a paper for reusable engineering insight, use the following conceptual separation:

```text
Paper evidence
↓
Source Claim
↓
Interpretation
↓
Generalized Methodology
```

Every step remains inspectable.

The resulting methodology record must retain provenance to the source material.

---

# 11. Universal Methodology Seed

Initialize the Method Bank with one reviewed universal methodology.

## Minimum Sufficient Context

### Aphorism

> Give each agent only the context required to perform its role reliably.

### Trigger

Whenever work is delegated to an agent or subagent.

### Scope

```text
universal
```

### Action Bias

Construct the task context from the assigned goal, required artifacts, relevant constraints and acceptance criteria.

### Verification

After task completion, check whether the agent had enough information to complete the assignment and whether additional supplied context materially contributed to the result.

---

# 12. Project Continuity

The repository root contains:

```text
AGENTS.md
WORKSTATE.md
```

These have different functions.

---

# 13. AGENTS.md

`AGENTS.md` is the stable agent entry point.

Keep it short.

It should identify:

- project purpose;
- important repository locations;
- build and test entry points;
- the project continuity procedure;
- Method Bank access;
- PaperPipe access;
- Context7 access.

For project-level continuation, it directs the agent to read `WORKSTATE.md`.

---

# 14. WORKSTATE.md

`WORKSTATE.md` represents the current operational state of the project.

Use this fixed structure:

```markdown
# Mission

# Current Objective

# Active Work

# Verified Completed Work

# Pending Work

# Current Decisions

# Evidence and Artifacts

# Verification Status

# Repository State

# Resume From Here

# Last Updated
```

---

# 15. Continuity Protocol

A project-level agent beginning a new session follows:

```text
Read AGENTS.md
↓
Read WORKSTATE.md
↓
Inspect repository state
↓
Verify relevant claims in WORKSTATE
↓
Resume from "Resume From Here"
```

Repository state includes relevant Git state, artifacts and tests.

`WORKSTATE.md` is an orientation artifact.

Code, tests, artifacts, Git history and the Method Bank provide verification.

---

# 16. WORKSTATE Update Rule

Update `WORKSTATE.md` at meaningful engineering checkpoints.

A checkpoint normally corresponds to one of:

- a completed independently verifiable task;
- a changed architectural decision;
- a newly discovered blocker;
- a validated experiment;
- a handoff between independent agents.

The new entry should allow a fresh project-level agent to continue without conversation history.

---

# 17. External Tool Setup

Kernel-Forge should prepare Codex to use:

## PaperPipe

Use its upstream-supported Codex integration.

Verify:

- CLI access;
- Codex skill access;
- paper ingestion;
- source retrieval;
- MCP retrieval tools when configured.

## Context7

Install its Codex-compatible documentation integration.

Verify that Codex can retrieve version-specific documentation for a known library.

---

# 18. Repository Layout

A minimal Forge workspace should resemble:

```text
kernel-forge/
├── AGENTS.md
├── WORKSTATE.md
├── README.md
├── .codex/
│   └── config.toml
├── method-bank/
│   ├── pyproject.toml
│   ├── src/
│   │   └── kernel_forge_method_bank/
│   │       ├── server.py
│   │       ├── db.py
│   │       ├── models.py
│   │       └── schema.sql
│   └── tests/
└── docs/
    ├── METHOD_SCHEMA.md
    └── TOOLING.md
```

Exact internal file subdivision may follow the existing engineering conventions of the implementation environment.

---

# 19. Acceptance Test A — Paper Grounding

Given a scientific paper:

1. add it to the local paper library;
2. retrieve a specific methodological passage;
3. preserve its source locator;
4. create one Method Bank candidate derived from it;
5. retrieve the candidate by a later methodological query;
6. follow its provenance back to the paper.

Pass condition:

\[
\boxed{
Method
\rightarrow
Source
}
\]

is reproducible.

---

# 20. Acceptance Test B — Method Retrieval

Store at least three methodologies with different scopes.

Issue a new engineering problem.

Retrieve relevant methods without loading the full source corpus.

Pass condition:

the agent can select and inspect the relevant methodology through the MCP interface.

---

# 21. Acceptance Test C — Continuity

Agent A performs part of a development task and updates repository state.

Start a fresh Agent B with no conversation history.

Agent B receives the repository.

It follows the project entry procedure and continues from the current engineering breakpoint.

Pass condition:

Agent B identifies:

- current objective;
- verified completed work;
- active unfinished work;
- next executable step;
- evidence required for completion.

---

# 22. Acceptance Test D — Minimum Sufficient Context

Delegate a bounded task to a fresh subagent.

Construct its task packet from:

- goal;
- required artifact locations;
- necessary constraints;
- acceptance criteria.

Evaluate whether the subagent completes the task without relying on unrelated project history.

Record the result as evidence associated with the universal methodology.

---

# 23. Forge Completion Criterion

Kernel-Forge v0.1 is complete when one fresh Codex session can:

```text
recover project state
↓
retrieve a relevant paper
↓
extract a source-grounded methodology
↓
store it in the Method Bank
↓
retrieve that methodology later
↓
use it in an engineering decision
↓
update WORKSTATE
```

with the full provenance chain remaining inspectable.

---

# 24. First Real Use

After acceptance tests pass, use Kernel-Forge as the development environment for Learner-Kernel.

The first development cycle should use the Forge itself to study and retrieve the research methods and engineering patterns required by the Kernel implementation.