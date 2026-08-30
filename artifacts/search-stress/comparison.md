# Evaluation comparison

Suite: `search-stress-v1`
Suite SHA-256: `6fc67011cd57f19f49343b756c4d2d4cb2805a65602cd96e98340021e17f6409`
Fixture registry SHA-256: `66c69b8c8e37c3698aae767c6653a54e1d2bbaf60177834809e62822e78fce98`
Evidence SHA-256:
- `evidence/policies/synthetic-policies.md`: `160f87edb1876007f753faf4f5e686117f9ca7853af2fae1792a8a9957ff24ba`
Seed: `2026`

| System | Balanced accuracy | Clean specificity | Mutant recall | Critical recall | Unknown rate | Replay success |
|---|---:|---:|---:|---:|---:|---:|
| Replay baseline | 0.500 | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | |
| Random baseline | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | |
| BFS ablation | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | |
| FidelityGate | 0.500 | 0.000 | 1.000 | 1.000 | 0.500 | 1.000 | |

## Per-case outcomes

| Case | Family | Truth | Replay baseline | Random baseline | BFS ablation | FidelityGate |
|---|---|---|---|---|---|---|
| env_900a | combinatorial_search | clean | ACCEPT | UNKNOWN | UNKNOWN | UNKNOWN |
| env_900b | combinatorial_search | mutated | ACCEPT | UNKNOWN | UNKNOWN | REJECT |

## Claim boundary

The smoke suite verifies a causal implementation path only. The full benchmark covers multiple paired mutation families, but it remains synthetic and does not by itself establish performance on proprietary production environments.
