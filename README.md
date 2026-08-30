# FidelityGate

FidelityGate is an evidence-bounded falsification agent for expert-built agent and reinforcement-learning environments. Before an environment is accepted for training or evaluation, it searches for reachable behavior that contradicts the approved source policy, minimizes the failure, and replays it three times. It returns `UNKNOWN` rather than turning incomplete evidence into certification.

## The user and bottleneck

The intended user is the environment engineer or domain expert approving a package assembled from policies, tools, rewards, state transitions, and reference trajectories. The common acceptance process replays expert happy paths. That proves intended behavior exists; it does not prove a shortcut is unreachable. FidelityGate tests the environment artifact itself, not the agent playing inside it.

The repository includes EnvMutationBench: 14 paired clean/mutated synthetic workflows covering authorization, identity, evidence, time, retries, ordering, tenant isolation, qualified review, memory, reward, and observability. Every pair shares expert traces that pass in both variants, so replay-only validation cannot identify the defect.

## Measured result

Primary evaluation, frozen seed and identical 28 cases:

| System | Balanced accuracy | Clean specificity | Mutant recall | Unknown rate |
|---|---:|---:|---:|---:|
| Expert-trajectory replay | 0.500 | 1.000 | 0.000 | 0.000 |
| Budgeted random exploration | 0.500 | 0.000 | 1.000 | 0.500 |
| Exhaustive BFS ablation | 1.000 | 1.000 | 1.000 | 0.000 |
| FidelityGate | **1.000** | **1.000** | **1.000** | **0.000** |

On four family-level holdouts, FidelityGate also scores 1.000 balanced accuracy. These are synthetic benchmark results, not an estimate of production performance.

The advanced search component has its own stress ablation. Under an identical 200-transition limit, BFS and random exploration miss a sparse mutant and return `UNKNOWN`; claim-directed frontier prioritization finds and verifies it in 30 transitions. It still returns `UNKNOWN` on the paired clean combinatorial case because completeness is not established. That is the intended safety behavior.

See the [full evidence memo](artifacts/envmutationbench/report.html), [comparison table](artifacts/envmutationbench/comparison.md), [stress evidence](artifacts/search-stress/comparison.md), and [reproduced negative result](artifacts/iterations/oracle-failure.json).

Watch the [2:54 artifact-driven demo](demo/fidelitygate-demo.mp4), with a separate [caption file](demo/fidelitygate-demo.srt). The video shows the real CLI, committed report, measured comparison, removed experiment, and clean-clone verification claim; it contains no mocked product screens.

## Why this is an agent

The falsification agent operates a bounded tool loop:

1. reset the unlabeled environment;
2. execute schema-valid actions;
3. check source-compiled claims after every transition;
4. remember canonical-state and claim-progress coverage;
5. prioritize the frontier autonomously;
6. shrink a contradiction;
7. replay it three times; and
8. choose `ACCEPT`, `REJECT`, or `UNKNOWN` under explicit rules.

It never receives benchmark ground truth. A representative 87-event product trajectory is committed at `trajectories/product-agent/env_900b-guided.json`. Five redacted coding-agent slices preserve problem selection through final verification under `trajectories/coding-agent/`.

## Quick start

Requirements: Python 3.11+, `uv` 0.12.7, Git; no API key or private data.

```bash
uv sync --frozen --all-groups
uv run fidelitygate compare \
  --suite evals/suites/envmutationbench.json \
  --output artifacts/envmutationbench
uv run pytest --cov=fidelitygate --cov-fail-under=85
```

Run one replayable product-agent trajectory:

```bash
uv run fidelitygate trace \
  --suite evals/suites/search-stress.json \
  --case-id env_900b \
  --output trajectories/product-agent/env_900b-guided.json
```

Or use the one-command paths:

```bash
bin/demo
bin/verify
```

## What is structurally necessary

- The data-only workflow DSL prevents fixtures from executing arbitrary code.
- Suite labels are stripped before a system is invoked.
- Source excerpts and anchors are validated and hashed before evaluation.
- Claim-directed coverage memory improves sparse falsification under a measured bound.
- Per-transition checks preserve ordering-sensitive evidence.
- Delta debugging turns noisy searches into minimal reviewer-usable witnesses.
- Triple replay gates rejection on deterministic evidence.
- Resource-bounded subprocesses receive no inherited credentials.
- `UNKNOWN` prevents depth, state, transition, execution, and replay failures from becoming acceptance.

No LLM is used where finite deterministic reasoning is stronger. An optional future semantic planner would be limited to proposing tests from natural-language sources; it could not issue verdicts.

## Repository map

- `src/fidelitygate/`: typed contracts, evidence compiler, DSL adapter, search agent, baselines, sandbox, evaluation, reports, and trajectories
- `evals/`: generated opaque fixtures, full/dev/holdout/stress suites, and mutation provenance
- `evidence/`: approved synthetic policy sources
- `artifacts/`: complete JSON, Markdown, and HTML evidence
- `tests/`: benchmark integrity, security, metrics, CLI, replay, and regression tests
- `docs/`: architecture, threat model, evaluation, reproduction, prior art, changelog, and submission guidance
- `demo/`: verified 2:54 video, captions, thumbnail, slide source, and reproducible build recipe
- `scripts/`: deterministic benchmark build, negative-result reproduction, demo build, and Codex trajectory export

## Decision boundary

- `ACCEPT`: no contradiction exists in the completely explored finite graph for the declared model and bounds.
- `REJECT`: a source-backed contradiction replays identically three times.
- `UNKNOWN`: evidence, search, execution, or replay is incomplete.

For consequential domains this is decision support only. A qualified human remains the approval authority.

## Main failure mode and hot take

The largest failure mode is a bad oracle, not a weak searcher. The first 28-case run falsely rejected one clean temporal workflow because the claim encoded final-state co-occurrence instead of event ordering, and returned `UNKNOWN` on another because the fixture allowed nonsensical post-terminal actions. Both failures are reproducible and documented.

Hot take: reliable environment evaluation starts by trying to falsify the evaluator. More simulated users do not repair an incorrect oracle; versioned counterexamples, explicit bounds, and honest abstention do.

## Documentation

- [Build plan](BUILD_PLAN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Evaluation contract](docs/EVALUATION.md)
- [Improvement changelog](docs/IMPROVEMENT_CHANGELOG.md)
- [Reproduction guide](docs/REPRODUCTION.md)
- [Prior art and licenses](docs/PRIOR_ART.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Agent use](docs/AGENT_USE.md)
- [Trajectory capture](docs/TRAJECTORIES.md)
- [Project provenance](docs/PROJECT_PROVENANCE.md)
