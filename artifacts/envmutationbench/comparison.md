# Evaluation comparison

Suite: `envmutationbench-v1`
Suite SHA-256: `26c65c267425b1dea219127f2d396817fb13b44ebd2fa29165457fbcc175d84b`
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
| env_002a | identity_separation | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_002b | identity_separation | mutated | ACCEPT | REJECT | REJECT | REJECT |
| env_003a | evidence_omission | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_003b | evidence_omission | mutated | ACCEPT | REJECT | REJECT | REJECT |
| env_004a | temporal_expiry | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_004b | temporal_expiry | mutated | ACCEPT | REJECT | REJECT | REJECT |
| env_005a | idempotency_failure | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_005b | idempotency_failure | mutated | ACCEPT | REJECT | REJECT | REJECT |
| env_006a | evidence_threshold | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_006b | evidence_threshold | mutated | ACCEPT | REJECT | REJECT | REJECT |
| env_007a | workflow_ordering | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_007b | workflow_ordering | mutated | ACCEPT | REJECT | REJECT | REJECT |
| env_008a | tool_precondition | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_008b | tool_precondition | mutated | ACCEPT | REJECT | REJECT | REJECT |
| env_009a | cross_tenant_confusion | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_009b | cross_tenant_confusion | mutated | ACCEPT | REJECT | REJECT | REJECT |
| env_010a | contract_evidence | clean | ACCEPT | UNKNOWN | ACCEPT | ACCEPT |
| env_010b | contract_evidence | mutated | ACCEPT | REJECT | REJECT | REJECT |
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
