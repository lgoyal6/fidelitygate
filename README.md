# FidelityGate

FidelityGate is an evidence-bounded acceptance gate for expert-built agent and reinforcement-learning environments. It tries to falsify an environment's behavioral claims before the environment is used for training or evaluation, then returns a replayable counterexample or an explicit `UNKNOWN` when the available evidence is insufficient.

## The user and bottleneck

The intended user is the engineer or domain expert approving an agent environment assembled from policies, source documents, tools, rewards, and reference trajectories. Today, validation often asks whether happy-path examples run and whether expert trajectories receive the intended reward. That misses reachable shortcuts: the examples can pass while a different tool sequence bypasses the source-backed policy.

The first vertical slice models a refund workflow. Both a clean environment and an approval-bypass mutant accept the same expert traces. The replay baseline therefore accepts both. FidelityGate explores reachable action sequences, checks a policy invariant after every transition, and minimizes a violating sequence into a deterministic witness.

This is deliberately a smoke proof, not the final benchmark. The full target is EnvMutationBench: public and synthetic environment packages with seeded, labeled defects across authorization, reward, tool semantics, temporal behavior, identity, evidence, and observability.

## What works now

- A fair replay-only baseline and FidelityGate receive the same suite and expert traces.
- A deterministic state-machine explorer checks the whole reachable space within the declared bound.
- A generic delta-debugging shrinker minimizes failures while preserving replayability.
- The evaluator reports balanced accuracy, mutant recall, clean specificity, replay success, and witness length.
- Every report records the suite hash and per-case evidence.
- A local Codex trajectory exporter creates judge-readable, redacted JSONL without committing raw session logs.

## Quick start

```bash
uv sync --all-groups
uv run fidelitygate compare --suite evals/suites/smoke.json --output artifacts/smoke
uv run pytest -q
```

Expected smoke result:

| System | Balanced accuracy | Clean specificity | Mutant recall |
|---|---:|---:|---:|
| Replay baseline | 0.500 | 1.000 | 0.000 |
| FidelityGate | 1.000 | 1.000 | 1.000 |

The two-case result proves only that the implementation distinguishes the selected minimal mutant. It is not evidence of generality. General claims are gated on the 10+ case benchmark described in [docs/EVALUATION.md](docs/EVALUATION.md).

## Repository map

- `src/fidelitygate/`: environment contract, refund adapter, baseline, explorer, shrinker, evaluator, and CLI
- `evals/suites/`: versioned benchmark manifests
- `tests/`: unit, integration, and regression tests
- `docs/`: architecture, threat model, prior art, build plan, evaluation, and reproduction guide
- `scripts/export_codex_trajectory.py`: redacted agent-trajectory export
- `trajectories/`: export documentation and representative sanitized traces

## Evidence and decision boundary

FidelityGate does not certify that an environment is correct. It emits:

- `ACCEPT` when no contradiction is found within a completely explored declared bound;
- `REJECT` when a deterministic, replayable counterexample contradicts a claim; or
- `UNKNOWN` when exploration, evidence, or replay is incomplete.

For consequential domains, this is decision support. A qualified human remains the approval authority.

## Project documents

- [Build plan](BUILD_PLAN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Evaluation contract](docs/EVALUATION.md)
- [Prior art and licenses](docs/PRIOR_ART.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Reproduction guide](docs/REPRODUCTION.md)
- [Trajectory capture](docs/TRAJECTORIES.md)
- [Agent use and instructions](docs/AGENT_USE.md)
- [Project provenance](docs/PROJECT_PROVENANCE.md)
- [Improvement changelog](docs/IMPROVEMENT_CHANGELOG.md)

## Main current failure mode and hot take

The largest failure mode is false confidence from an incomplete action model: a checker can exhaust its model while omitting the real shortcut. The hot take is that stronger agent evaluators need better uncertainty accounting more than they need more simulated users. Exhaustion over an undocumented abstraction should produce `UNKNOWN`, not a certification badge.
