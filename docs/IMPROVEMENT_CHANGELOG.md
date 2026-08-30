# Improvement changelog

Every retained component is connected to an artifact or regression test. The same paired cases and frozen metric are used wherever the comparison is meaningful.

| Stage | What you tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | Replayed the expert-provided trajectories, matching the common environment acceptance process. | `artifacts/envmutationbench/baseline.json`: balanced accuracy 0.500; accepts all 14 clean and all 14 defective packages. | Happy paths prove intended behavior exists but cannot show that shortcuts are unreachable. Keep as the fair primary baseline. |
| Iteration 1 | Added bounded BFS, per-transition claims, shrinking, and replay to test the complete reachable environment rather than examples. | Reproducible flawed-oracle result in `artifacts/iterations/oracle-failure.json`: balanced accuracy 0.929, one false rejection, one `UNKNOWN`. | The search exposed two benchmark defects. Do not tune the agent around a bad oracle; repair the evaluation representation and preserve the negative result. |
| Iteration 2 | Replaced temporal final-state co-occurrence with an explicit `access_after_expiry` event and made password reset terminal. Added mutation-integrity tests for every pair. | `artifacts/envmutationbench/bfs-ablation.json`: balanced accuracy 1.000; all 28 outcomes correct and all rejection witnesses replay. | Keep typed event semantics and terminal-state conformance. The main surprise was that benchmark engineering, not search, was the limiting factor. |
| Iteration 3 | Added claim-directed best-first frontier priority because plain BFS expands irrelevant combinatorial state uniformly. | `artifacts/search-stress/`: BFS and random return `UNKNOWN` on the mutant at 200 transitions; FidelityGate rejects it in 30. | Keep. On the primary suite BFS and guided both score 1.000, so the stress ablation—not component count—is the justification. |
| Iteration 4 | Added evidence compilation, evaluator-only label isolation, a data-only DSL, credential-minimized worker limits, and three-way failure handling. | Evidence/path/label tests plus timeout, worker-crash, invalid-output, and shell-shaped-action regressions; 31 tests and over 90% coverage. | Keep. These controls do not inflate accuracy; they make each verdict falsifiable and safe to reproduce. |
| Iteration 5 | Split four mutation families before final evidence generation and ran them as a family-level holdout. | `artifacts/holdout/fidelitygate.json`: balanced accuracy 1.000 on 8 cases across qualified review, memory, reward, and observability. | Keep the split and claim only synthetic family holdout, not independent production validation. |
| Final | Combined source compilation, unlabeled agent input, claim-directed state coverage, shrink/replay verification, safe abstention, and evidence-first reports. | `artifacts/envmutationbench/`: replay 0.500 → FidelityGate 1.000 balanced accuracy; 14/14 mutant recall, 14/14 clean specificity, 3/3 replay for every witness. | Main contribution: whole-environment falsification converts invisible policy shortcuts into small, cited, reproducible review artifacts. |

## Removed or bounded experiments

- **Counterexample shrinking as an accuracy feature:** on breadth-first search, the discovered smoke witness was already shortest-depth, so shrinking removed zero actions. It remains only as an artifact-quality and future-search safeguard; its accuracy contribution is not claimed.
- **Random search as acceptance:** random search found all small-suite mutants but cannot prove clean cases, so treating “no failure found” as acceptance would be unsafe. It now returns `UNKNOWN` for those cases.
- **LLM verdict agent:** rejected before implementation. Typed finite claims and replay are exact; an LLM in the verdict path would add unsupported variability. A future semantic agent may propose claims or tests but cannot decide.
- **Arbitrary Python adapters:** rejected until a true hostile-code sandbox exists. The current worker boundary interprets a code-free DSL and does not claim general code isolation.

## Main failure mode

The most dangerous failure is evaluator self-consistency: a searcher can perfectly optimize an incorrect invariant and produce convincing evidence for the wrong rule. The first run demonstrated this with temporal ordering. FidelityGate therefore hashes source excerpts, separates event semantics from final-state co-occurrence, preserves failures, and returns `UNKNOWN` when the abstraction is incomplete.

## Hot take

The primary moat in agent evaluation is not the number of simulated users or judge-model calls. It is how quickly the evaluation stack can produce and survive a counterexample against its own assumptions. A leaderboard score without a minimal replay and a source-backed oracle is weaker evidence than one embarrassing, reproducible failure.
