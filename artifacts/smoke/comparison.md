# Evaluation comparison

Suite: `refund-approval-smoke-v2`
Suite SHA-256: `84188b0df6b2792d5bec71101bbd951255c2b8a65c826f28142aa98b49a484f9`
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
| env_001a | authorization_bypass | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_001b | authorization_bypass | mutated | ACCEPT | REJECT | REJECT | REJECT |

## Claim boundary

The smoke suite verifies a causal implementation path only. The full benchmark covers multiple paired mutation families, but it remains synthetic and does not by itself establish performance on proprietary production environments.
