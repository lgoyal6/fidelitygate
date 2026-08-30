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
- Trajectory exporter was exercised against the active append-only Codex session and produced valid redacted JSONL plus provenance manifests.

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
- Thirty-two tests pass at 92.93% package coverage; strict mypy, Ruff, deterministic generation, and committed-artifact reproduction pass locally.
- The same one-command gate passed from a fresh temporary clone in 16.7 seconds with byte-identical evidence.
- Five representative coding-agent slices cover problem selection, architecture, the baseline harness, benchmark failures, and final verification. Common credentials, home paths, and the GitHub device code are redacted; raw logs remain outside Git.
- The generated 174.5-second H.264/AAC demo passed a full decode, stream probe, duration gate, and six-frame visual review. Its terminal sequence runs the actual baseline and stress-case trace commands.
- Pushed the complete branch to private GitHub `main`; local, tracking, and remote refs matched `608019ae801a4b9bef050b8a804c782b8d2b029c`. GitHub Actions run `33325420869` passed every verification step in 35 seconds.
