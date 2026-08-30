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
