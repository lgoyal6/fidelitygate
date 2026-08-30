# Evaluation comparison

Suite: `envmutationbench-holdout-v1`
Suite SHA-256: `1de27eb8818947fc48f3eb72f63b0f1943f239c7f4f305078a10afe9ea13bf6a`
Fixture registry SHA-256: `66c69b8c8e37c3698aae767c6653a54e1d2bbaf60177834809e62822e78fce98`
Evidence SHA-256:
- `evidence/policies/synthetic-policies.md`: `160f87edb1876007f753faf4f5e686117f9ca7853af2fae1792a8a9957ff24ba`
Seed: `2026`

| System | Balanced accuracy | Clean specificity | Mutant recall | Critical recall | Unknown rate | Replay success |
|---|---:|---:|---:|---:|---:|---:|
| Replay baseline | 0.500 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | |
| Random baseline | 0.500 | 0.000 | 1.000 | 1.000 | 0.500 | 1.000 | |
| BFS ablation | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | |
| FidelityGate | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | |

## Per-case outcomes

| Case | Family | Truth | Replay baseline | Random baseline | BFS ablation | FidelityGate |
|---|---|---|---|---|---|---|
| env_011a | qualified_review_gate | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_011b | qualified_review_gate | mutated | ACCEPT | REJECT | REJECT | REJECT |
| env_012a | cross_episode_memory | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_012b | cross_episode_memory | mutated | ACCEPT | REJECT | REJECT | REJECT |
| env_013a | reward_policy_mismatch | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_013b | reward_policy_mismatch | mutated | ACCEPT | REJECT | REJECT | REJECT |
| env_014a | observability_omission | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_014b | observability_omission | mutated | ACCEPT | REJECT | REJECT | REJECT |

## Claim boundary

The smoke suite verifies a causal implementation path only. The full benchmark covers multiple paired mutation families, but it remains synthetic and does not by itself establish performance on proprietary production environments.
