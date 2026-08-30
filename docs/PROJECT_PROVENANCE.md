# Project provenance

## Created for the competition

All source code, synthetic refund fixtures, tests, benchmark manifests, result artifacts, documentation, trajectory-export code, and CI configuration in this repository were created for the micro1 Frontier Engineering Challenge 2026 after problem approval.

## Pre-existing material

No pre-existing product code or proprietary dataset was imported. The project uses the public Python dependencies pinned in `uv.lock` and the prior-art research listed in [PRIOR_ART.md](PRIOR_ART.md). Architecture concepts were studied from those systems; their source code was not copied.

The synthetic policy and environments were authored solely for the benchmark and contain no private or consequential user data.

## Evidence status

- The two-case smoke, 28-case EnvMutationBench, 8-case family holdout, and 2-case stress results are generated and committed.
- Claim-directed priority is supported by a budgeted stress ablation; primary BFS and FidelityGate both score 1.000.
- Source/anchor/excerpt compilation, opaque fixtures, label-isolated system input, data-only adapter execution, worker limits, triple replay, and three-way verdicts are implemented and tested.
- General production performance, independent mutation review, stochastic environments, arbitrary-code adapters, natural-language claim extraction, and qualified-reviewer time savings are not established.
- Raw coding-agent sessions remain outside Git; only manually reviewed redacted exports are eligible for the submission.
