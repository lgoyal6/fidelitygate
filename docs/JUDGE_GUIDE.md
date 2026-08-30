# Judge guide

## Ninety-second path

1. Read the user/bottleneck and result at the top of `README.md`.
2. Open `artifacts/envmutationbench/report.html`.
3. Run `bin/demo` to see replay miss the refund bypass and the agent produce a verified witness.
4. Inspect `trajectories/product-agent/env_900b-guided.json` for the complete tool loop.
5. Run `bin/verify` to reproduce every committed primary, stress, and holdout artifact.

## Claims to verify

| Claim | Evidence |
|---|---|
| Replay-only acceptance misses every seeded shortcut. | `artifacts/envmutationbench/baseline.json` |
| FidelityGate separates all 14 clean/mutated pairs. | `artifacts/envmutationbench/fidelitygate.json` |
| Results persist across four held-out mutation families. | `artifacts/holdout/fidelitygate.json` |
| Claim-directed priority changes the bounded stress result. | `artifacts/search-stress/bfs-ablation.json` versus `fidelitygate.json` |
| Every rejection is source-cited and replays three times. | Witness objects in final JSON and HTML evidence memo |
| Benchmark labels do not enter the system interface. | `CaseSpec.audit_input()` and `test_audit_input_excludes_ground_truth` |
| Evidence and fixtures are versioned rather than trusted prose. | Suite, registry, and evidence hashes in every report |
| The negative oracle experiment was not hidden. | `artifacts/iterations/oracle-failure.json` |
| A clean checkout reproduces the result. | `bin/verify` and successful GitHub Actions run `33325420869` |

## Claim limits

- The benchmark is synthetic and repository-authored.
- Holdout families were separated before final artifact generation but are not independent external validation.
- The worker protects a data-only DSL; it is not a general untrusted-code sandbox.
- No qualified-reviewer time study has been run.
- The product never takes a consequential action and does not replace a reviewer.
