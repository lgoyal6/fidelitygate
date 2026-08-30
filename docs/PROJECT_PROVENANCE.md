# Project provenance

## Created for the competition

All source code, synthetic refund fixtures, tests, benchmark manifests, result artifacts, documentation, trajectory-export code, and CI configuration in this repository were created for the micro1 Frontier Engineering Challenge 2026 after problem approval.

## Pre-existing material

No pre-existing product code or proprietary dataset was imported. The project uses the public Python dependencies pinned in `uv.lock` and the prior-art research listed in [PRIOR_ART.md](PRIOR_ART.md). Architecture concepts were studied from those systems; their source code was not copied.

The synthetic policy and environments were authored solely for the benchmark and contain no private or consequential user data.

## Evidence status

- The two-case smoke results are generated and committed.
- General detector performance is not yet established.
- Advanced exploration, arbitrary-adapter sandboxing, natural-language evidence compilation, and the full EnvMutationBench remain planned until implemented and verified.
- Raw coding-agent sessions remain outside Git; only manually reviewed redacted exports are eligible for the submission.
