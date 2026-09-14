# Agent Handoff Index

Read `WORKSTATE.md` for current objective, verified status and exact next step. It is the authoritative operational record; code, data and tests verify its claims.

## Recovery order
1. `WORKSTATE.md`
2. `.agent-handoff/snapshot.md`
3. `.agent-handoff/risks.md`
4. `.agent-handoff/backlog.md`
5. `.agent-handoff/validation.md` when evidence affects the task
6. `.agent-handoff/decisions.md` when changing durable behavior
7. `.agent-handoff/workspace.md` when locating commands or artifacts

Read work-log/archive only for relevant history. Current state is replaced, not appended. At checkpoints update the smallest relevant evidence files and WORKSTATE, run the installed agent-handoff maintenance script, and re-read changes before reporting completion. Keep credentials and full logs out of continuity files.

Project rules: `AGENTS.md`. This repository currently targets Codex; no Claude-specific rules were installed.
