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

## Product agents

The current smoke solution is deterministic and uses no LLM product agent. This is intentional: an LLM is not structurally required to enumerate a finite action space or evaluate a typed invariant. A future semantic-adversary agent may propose tests from natural-language sources, but it cannot issue a verdict; its proposals must pass schema validation, execute in the adapter, and produce a replayable contradiction.

No multi-agent orchestration is claimed in the current implementation.
