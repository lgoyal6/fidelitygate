# Build notes

## 2026-08-30 — repository bootstrap

- Product locked: FidelityGate, an evidence-bounded acceptance gate for expert-built agent/RL environments.
- First causal test: expert trajectories pass both clean and authorization-bypass refund environments; directed bounded exploration must separate them.
- Primary metric frozen before implementation: balanced accuracy, with `UNKNOWN` counted incorrect.
- Advanced components are deferred until a benchmark failure justifies them.
- Raw Codex session capture verified locally; repository includes a redacting exporter instead of raw logs.

## 2026-08-30 — evaluation-first vertical slice

- Replay baseline accepted both clean and admin-bypass cases: balanced accuracy 0.500.
- Bounded graph exploration accepted the clean case and rejected the mutant: balanced accuracy 1.000.
- Replayed witness: `submit_refund(amount=1500)` then `issue_refund(role='admin')`.
- Clean graph completed in 8 states and 48 transitions; mutant contradiction appeared after 6 states and 18 transitions.
- Nine tests pass at 76% package coverage; Ruff formatting/lint and strict mypy pass.
- Trajectory exporter was exercised against the active 1,800+ record Codex session and produced valid redacted JSONL plus a provenance manifest. The export remains outside Git pending manual review and representative slicing.

## 2026-08-30 — EnvMutationBench and evaluator self-test

- Replaced the refund-specific adapter with a strict data-only workflow DSL and opaque fixture registry.
- Generated 14 clean/mutated pairs (28 primary cases), 10-family development and 4-family holdout splits, plus a combinatorial stress pair.
- Every expert trace passes both members of its pair; every minimal mutation trigger is safe on clean and contradictory on mutated.
- Initial full audit scored 0.929: a clean temporal case was falsely rejected and a clean recovery case returned `UNKNOWN`. The former encoded final-state co-occurrence instead of ordering; the latter allowed post-terminal transitions.
- Fixed the benchmark semantics and preserved the failed iteration in `artifacts/iterations/oracle-failure.json` with a one-command reproducer.

## 2026-08-30 — advanced search, controls, and finish

- Added claim-directed frontier priority. On the 200-transition stress mutant, BFS/random return `UNKNOWN`; guided search rejects in 30 transitions. The clean stress case remains `UNKNOWN` for all bounded explorers.
- Added source path/anchor/excerpt validation and hashes, evaluator-only label isolation, triple replay, and full `ACCEPT`/`REJECT`/`UNKNOWN` failure handling.
- Added credential-minimized subprocess execution for the data-only DSL with timeout and POSIX resource limits. Explicitly did not claim general hostile-code isolation.
- Added JSON, Markdown, and print-ready HTML evidence, family holdout results, product-agent trajectories, judge guide, five-minute demo script, and submission copy.
- Thirty-one tests pass with over 90% package coverage; strict mypy, Ruff, deterministic generation, and committed-artifact reproduction pass locally.
