# Agent use and public instructions

## Coding agent used

Codex CLI is the coding agent used to research, design, implement, test, and document this repository. The user supplied the following governing instruction envelope before implementation:

- Research micro1 and its evaluation pattern before selecting a problem.
- Treat prior art as the first filter and explicitly kill ideas without a specific gap.
- Optimize for rubric score and engineering quality without time-based scope cuts.
- Use agents only where structurally necessary; every component needs measured justification.
- Freeze the primary metric and build the evaluation harness before the advanced solution.
- Use the same cases for baseline and final system and include all failures.
- Use public or synthetic data, sandbox consequential actions, and keep a qualified human in control.
- Preserve reproducibility, agent trajectories, and evidence from the first command.
- Stop before architecture/code until the user explicitly approves a problem.
- After approval, create the repository, publish the build plan and required documentation, implement the proven core path, verify it, and push it.

The selected problem and implementation were explicitly approved before repository creation. The redacted trajectory described in [TRAJECTORIES.md](TRAJECTORIES.md) is the evidence source for individual tool calls, feedback, retries, and verification results.

## Product agent

FidelityGate's falsification agent receives this stable public instruction:

> Try to falsify every source-backed environment claim within the declared bounds. Use only the unlabeled case, action interface, observations, coverage memory, claim checker, shrinker, and replay tool. Reject only for a contradiction that replays identically three times; accept only after the finite reachable graph is complete; otherwise return UNKNOWN.

The agent is deterministic and non-LLM because finite state exploration and typed invariants have an exact oracle. It autonomously operates reset, execution, claim-check, coverage-memory, frontier-priority, shrink, replay, and verdict tools. Its decision policy is claim-directed best-first search with explicit limits.

A future semantic-adversary LLM may propose tests from natural-language sources, but it cannot issue a verdict; proposals must pass schema validation, execute in the adapter, and produce a replayable contradiction. No multi-agent orchestration is claimed because the measured task does not require it.
