# Five-minute demo script

## 0:00–0:35 — problem

“Environment teams replay expert trajectories before using an agent or RL environment. That proves the intended route works. It does not prove a shortcut is impossible. FidelityGate audits the environment itself and returns a source-cited replay, not a vibe-based score.”

Show the synthetic refund policy sentence and the clean/mutated pair. Emphasize that the same approved traces pass in both.

## 0:35–1:20 — simple baseline

Run:

```bash
uv run fidelitygate eval --suite evals/suites/smoke.json --system replay-baseline
```

Point to both `ACCEPT` verdicts and balanced accuracy 0.500. “This is the bottleneck in one table.”

## 1:20–2:30 — realistic end-to-end execution

Run:

```bash
uv run fidelitygate trace \
  --suite evals/suites/search-stress.json \
  --case-id env_900b \
  --output /tmp/fidelitygate-trace.json
```

Open the trajectory and show reset, actions, claim-progress coverage, contradiction, shrinking, 3/3 replay, and `REJECT`. Then show the witness:

1. `submit_sensitive_request`
2. `issue_sensitive_result(role='admin')`

Show the approved source excerpt and observed forbidden state in the final outcome.

## 2:30–3:25 — engineering choices

Use the architecture diagram. Explain only components with evidence:

- labels stripped before the agent;
- data-only adapter in a resource-bounded worker;
- source excerpt and hash validation;
- claim-directed coverage memory;
- shrink and triple replay;
- `UNKNOWN` for incomplete bounds.

Compare stress results: BFS/random miss the mutant at 200 transitions; guided finds it in 30. Point out that the clean stress case remains `UNKNOWN`, proving the system does not turn search failure into acceptance.

## 3:25–4:10 — final measured comparison

Open `artifacts/envmutationbench/report.html`.

- Replay: 0.500 balanced accuracy.
- FidelityGate: 1.000 across 28 paired cases.
- Four held-out families: 1.000 across 8 cases.
- Every final witness: 3/3 replay.

Say explicitly: “This is synthetic benchmark evidence, not a production-performance estimate.”

## 4:10–4:42 — removed experiment

Show `artifacts/iterations/oracle-failure.json`.

“The first run scored 0.929 because my temporal oracle was wrong: access before expiry followed by expiry looked like access after expiry. The agent was right to expose the bad benchmark. I replaced final-state co-occurrence with an ordering event and made terminal transitions explicit.”

Mention that shrinking did not shorten the BFS smoke witness, so no accuracy benefit is claimed for it.

## 4:42–5:00 — hot take and reproducibility

“The hard part of agent evaluation is not generating more scenarios. It is falsifying the evaluator’s own assumptions. A score without a minimal replay and a source-backed oracle is weak evidence.”

End on:

```bash
bin/verify
```

and the line: `All checks and committed evidence reproductions passed.`
