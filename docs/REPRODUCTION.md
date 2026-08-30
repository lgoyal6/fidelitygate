# Reproduction guide

## Requirements

- macOS or Linux
- Python 3.11 or newer
- `uv` 0.8 or newer
- Git

No model API key, credential, network service, or private dataset is required for the smoke evaluation.

## Clean setup

```bash
git clone https://github.com/lgoyal6/fidelitygate.git
cd fidelitygate
uv sync --frozen --all-groups
```

## Run the baseline

```bash
uv run fidelitygate eval \
  --suite evals/suites/smoke.json \
  --system replay-baseline \
  --output artifacts/smoke/baseline.json
```

Expected: balanced accuracy `0.500`; the baseline incorrectly accepts the approval-bypass mutant because all supplied expert traces pass.

## Run FidelityGate

```bash
uv run fidelitygate eval \
  --suite evals/suites/smoke.json \
  --system fidelitygate \
  --output artifacts/smoke/fidelitygate.json
```

Expected: balanced accuracy `1.000`; the mutant is rejected with a replayable witness while the clean environment is accepted after complete bounded exploration.

## Run the comparison and tests

```bash
uv run fidelitygate compare --suite evals/suites/smoke.json --output artifacts/smoke
uv run ruff check .
uv run mypy src scripts
uv run pytest --cov=fidelitygate --cov-report=term-missing
```

The comparison command writes JSON results and `comparison.md`. Runtime should be below a few seconds on a typical laptop and model cost is exactly `$0` for the deterministic smoke slice.

## Replay a finding

The final-system JSON includes each witness as ordered actions plus expected and observed values. The comparison run replays every deterministic witness before allowing `REJECT`; failed replay becomes `UNKNOWN`.

## Important claim boundary

The smoke suite has two cases. Reproducing it proves the code path and the selected counterexample, not general detector performance. General metrics require the versioned 10+ case EnvMutationBench suite.
