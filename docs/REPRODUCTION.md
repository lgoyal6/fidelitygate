# Reproduction guide

## Clean-environment requirements

- macOS or Linux
- Git
- Python 3.11 or newer
- `uv` 0.12.7

No model API key, private dataset, credential, network service, database, container, or cloud account is required. All workflows and policies are synthetic.

## Setup

```bash
git clone https://github.com/lgoyal6/fidelitygate.git
cd fidelitygate
uv sync --frozen --all-groups
```

## One-command verification

```bash
bin/verify
```

This runs formatting, lint, strict type checks, tests with an 85% coverage floor, benchmark-generation freshness, and fresh full/stress/holdout comparisons. It byte-compares the regenerated JSON, Markdown, and HTML artifacts with the committed evidence.

Expected terminal line:

```text
All checks and committed evidence reproductions passed.
```

Typical local runtime is 10–20 seconds on an Apple Silicon laptop. The solution makes zero model calls and has exactly $0 model cost. A clean temporary clone completed this gate in 16.7 seconds on the development machine and reproduced committed JSON, Markdown, and HTML evidence byte-for-byte.

## Baseline

```bash
uv run fidelitygate eval \
  --suite evals/suites/envmutationbench.json \
  --system replay-baseline \
  --output /tmp/fidelitygate-baseline.json
```

Expected primary result: balanced accuracy `0.500`, clean specificity `1.000`, mutant recall `0.000`.

## Final agent

```bash
uv run fidelitygate eval \
  --suite evals/suites/envmutationbench.json \
  --system fidelitygate \
  --output /tmp/fidelitygate-final.json
```

Expected primary result: balanced accuracy `1.000`, clean specificity `1.000`, mutant recall `1.000`, replay success `1.000`.

## Complete comparison

```bash
uv run fidelitygate compare \
  --suite evals/suites/envmutationbench.json \
  --output artifacts/envmutationbench
```

Outputs:

- `baseline.json`
- `random-baseline.json`
- `bfs-ablation.json`
- `fidelitygate.json`
- `comparison.md`
- `report.html`

The same command works with:

- `evals/suites/envmutationbench-holdout.json`
- `evals/suites/search-stress.json`
- `evals/suites/smoke.json`

## Product-agent trajectory

```bash
uv run fidelitygate trace \
  --suite evals/suites/search-stress.json \
  --case-id env_900b \
  --output /tmp/env_900b-guided.json
```

Expected: verdict `REJECT`, 30 explored transitions, a two-action witness, and an ordered tool trajectory including reset, execution, coverage, prioritization, claim check, shrinking, three replays, and verdict.

## Benchmark provenance and negative result

Verify generated benchmark bytes:

```bash
uv run python scripts/build_benchmark.py --check
```

Reproduce the removed flawed-oracle iteration:

```bash
uv run python scripts/reproduce_oracle_failure.py \
  --output /tmp/oracle-failure.json
```

Expected: balanced accuracy `0.929`, with clean temporal case `REJECT` and clean recovery case `UNKNOWN`.

## Data and versioning

- Policy evidence: `evidence/policies/synthetic-policies.md`
- Fixture registry: `evals/fixtures/envmutationbench.json`
- Mutation provenance: `evals/mutations.json`
- Suite and registry SHA-256 values are embedded in every result.
- Evidence paths, anchors, exact excerpts, and file hashes are checked before any agent runs.
- Dependency versions are pinned in `uv.lock`.

## Claim boundary

Reproduction proves the implementation and synthetic results. The benchmark was authored in this repository and the four-family holdout is not independent external validation. Production performance would require approved operational sources, independently authored environment packages and mutations, qualified reviewers, and a stronger sandbox before arbitrary adapter code is accepted.

## Demo video

The checked-in `demo/fidelitygate-demo.mp4` is 174.5 seconds, 1600×900 H.264 video with 48 kHz AAC audio and burned captions. Rebuild it on macOS with `uv run python scripts/build_demo_video.py`; see `demo/README.md` for platform tools. Video generation is deliberately separate from `bin/verify` because it depends on macOS speech synthesis and presentation tooling, while the scored benchmark gate remains cross-platform.
