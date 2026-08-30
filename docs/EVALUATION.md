# Evaluation contract

## Frozen primary metric

Balanced accuracy over paired environments labeled `clean` or `mutated`:

```text
balanced_accuracy = (clean_specificity + mutant_recall) / 2
```

`ACCEPT` is correct only for clean cases and `REJECT` only for mutated cases. `UNKNOWN` is deliberately incorrect for the primary metric. This preserves safe abstention without letting a system inflate its score by refusing every decision.

## Good result, defined before advanced evaluation

- Improve balanced accuracy over expert-trajectory replay on identical cases.
- Preserve clean specificity; rejecting everything is not useful.
- Replay every deterministic rejection identically three times.
- Localize the exact source-backed claim and transition sequence.
- Make incomplete search/evidence explicit as `UNKNOWN`.
- Preserve the result on family-level holdouts.
- Show that every advanced strategy improves a measured frontier or remove it.

## Suites

| Suite | Cases | Purpose |
|---|---:|---|
| `smoke.json` | 2 | Causal clean/refund-bypass path used to validate the harness. |
| `envmutationbench-dev.json` | 20 | Ten paired families used while implementing and debugging. |
| `envmutationbench-holdout.json` | 8 | Four held-out families: qualified review, memory, reward, observability. |
| `envmutationbench.json` | 28 | Complete primary comparison across 14 balanced pairs. |
| `search-stress.json` | 2 | Combinatorial decoys under a fixed 200-transition bound. |

Every fixture ID is opaque. Ground truth, family, and criticality are stripped into `AuditCaseSpec` before a system runs. A regression test verifies this interface boundary.

## Mutation families

Authorization bypass, separation of duties, evidence omission, temporal expiry, idempotency, evidence thresholds, workflow ordering, tool preconditions, cross-tenant identity, contract evidence, qualified review, cross-episode memory, reward-policy mismatch, and observability omission.

Every pair has:

- one clean and one defective fixture;
- identical source-backed claims and expert traces;
- traces that pass in both fixtures;
- a provenance record for the semantic mutation;
- a minimal trigger that is safe in the clean fixture and contradictory in the mutant;
- strict generation and integrity tests.

The benchmark is synthetic and authored in the same repository. Family holdout reduces direct iteration leakage but is not independent external validation. Qualified human review remains a submission task.

## Systems and fairness

All systems receive the same unlabeled case, fixture interface, claims, expert traces, and resource limits.

1. **Replay baseline:** runs only the supplied expert trajectories.
2. **Random baseline:** samples deterministic random sequences with the same per-case transition bound; no finding becomes acceptance, so clean cases end as `UNKNOWN`.
3. **BFS ablation:** exhaustive breadth-first graph exploration, per-transition claims, shrinking, and triple replay.
4. **FidelityGate:** the same verified kernel with a best-first frontier prioritized by how many source-claim clauses a state satisfies.

The primary suite is intentionally small enough for BFS to complete, isolating the value of whole-environment exploration over replay. The search-stress suite isolates frontier strategy: at 200 transitions, BFS and random miss the sparse mutant; FidelityGate finds it in 30. Neither exploration system accepts the clean stress case because neither completes the graph.

## Results

### Primary 28-case suite

| System | Balanced accuracy | Clean specificity | Mutant recall | Unknown rate |
|---|---:|---:|---:|---:|
| Replay | 0.500 | 1.000 | 0.000 | 0.000 |
| Random | 0.500 | 0.000 | 1.000 | 0.500 |
| BFS ablation | 1.000 | 1.000 | 1.000 | 0.000 |
| FidelityGate | 1.000 | 1.000 | 1.000 | 0.000 |

All 14 final witnesses replay 3/3 times; median minimized witness length is 2 actions. Four-family holdout balanced accuracy is 1.000.

### Stress suite

| System | Clean verdict | Mutant verdict | Mutant transitions | Mutant recall |
|---|---|---|---:|---:|
| Random | UNKNOWN | UNKNOWN | 200 | 0.000 |
| BFS ablation | UNKNOWN | UNKNOWN | 200 | 0.000 |
| FidelityGate | UNKNOWN | REJECT | 30 | 1.000 |

## Secondary metrics

- critical-mutant recall;
- family recall;
- unknown rate;
- replay success rate;
- median witness length;
- explored states and transitions;
- claim checks;
- source, suite, and fixture hashes;
- eventual qualified-reviewer time, runtime, and model cost.

The deterministic implementation has zero model cost. Runtime is reported by the reproduction guide rather than embedded as a machine-dependent score.

## Challenging case and revealed failure

The first 28-case run scored 0.929, not 1.000. A clean temporal workflow was falsely rejected because the oracle treated `accessed=true` plus `expired=true` as proof of post-expiry access even when access occurred first. A recovery workflow returned `UNKNOWN` because verification remained possible after terminal password reset, creating new depth-four states.

The repaired benchmark records an explicit `access_after_expiry` event and makes reset terminal. The original failure is reproducible with:

```bash
uv run python scripts/reproduce_oracle_failure.py
```

This was an evaluation defect, not a model miss. It is preserved because the practical lesson is central: falsify the benchmark oracle before trusting a detector score.
