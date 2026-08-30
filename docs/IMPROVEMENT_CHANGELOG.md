# Improvement changelog

This file is evidence-bound. Stages after the smoke implementation remain planned until their benchmark artifacts exist.

| Stage | What you tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | Replayed the expert-provided trajectories, matching the common environment acceptance process. | `artifacts/smoke/baseline.json`: balanced accuracy 0.500; it accepts both the clean and bypass environments. | Expert examples establish intended behavior but do not expose the unrepresented shortcut. |
| Iteration 1 | Added exhaustive bounded transition exploration and checked the policy invariant after every action. | `artifacts/smoke/fidelitygate.json`: balanced accuracy 1.000 on the pair; clean accepted and mutant rejected. | Keep for the benchmark expansion; the result is causal smoke evidence, not a general performance estimate. |
| Iteration 2 | Added counterexample shrinking and replay verification so findings are usable and deterministic. | The witness replays and contains two actions. BFS had already found a shortest-depth path, so shrinking reduced it by zero actions in this case. | Keep replay as a verdict gate. Treat shrinker's usefulness as unproven until a noisier search strategy produces longer failures. |
| Iteration 3 | Planned: compare coverage-guided, archive, symbolic, and semantic strategies on held-out mutation families. | Not yet measured. | No strategy advances on architectural appeal alone. |
| Final | Planned: combine only changes that improve the frozen evaluation contract. | Full EnvMutationBench comparison and ablation table. | Identify the causal contribution and report failures. |

## Main failure mode

An incomplete action or state abstraction can make exhaustive search look stronger than it is. Search completion is meaningful only relative to the declared model, so missing coverage or evidence must produce `UNKNOWN`.

## Hot take

The next reliability moat for agent environments is not another average task-success leaderboard. It is versioned falsification evidence: the smallest policy-violating behavior an environment permits, tied to the source claim it contradicts and replayable by a skeptical reviewer.
