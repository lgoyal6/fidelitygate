# Smoke evaluation comparison

Suite: `refund-approval-smoke-v1`
Suite SHA-256: `34596ec01219ef2fad9daf3e488f921a9eb31ee116de4e7ddcbf991a4e7b6312`

| System | Balanced accuracy | Clean specificity | Mutant recall | Unknown rate | Replay success |
|---|---:|---:|---:|---:|---:|
| Replay baseline | 0.500 | 1.000 | 0.000 | 0.000 | 1.000 | |
| FidelityGate | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | |
| Change | +0.500 | +0.000 | +1.000 | +0.000 | +0.000 | |

## Claim boundary

This two-case smoke suite demonstrates the causal failure of replay-only validation on one approval-bypass mutant and verifies the end-to-end harness. It does not estimate general detector performance.
