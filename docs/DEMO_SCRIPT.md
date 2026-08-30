# 2:54 demo script

## 0:00–0:19 — problem

“Environment teams replay expert trajectories before using an agent or RL environment. That proves the intended route works. It does not prove a shortcut is impossible. FidelityGate audits the environment itself and returns a source-cited replay, not a vibe-based score.”

Show the synthetic policy and explain that identical expert traces pass the clean and mutated pair.

## 0:19–0:42 — baseline and end-to-end execution

Run the replay baseline:

```bash
uv run fidelitygate eval --suite evals/suites/smoke.json --system replay-baseline
```

Point to both `ACCEPT` verdicts and balanced accuracy 0.500. Then run the stress mutant:

```bash
uv run fidelitygate trace \
  --suite evals/suites/search-stress.json \
  --case-id env_900b \
  --output /tmp/fidelitygate-trace.json
```

Show `REJECT`, 30 explored transitions, the two-action witness, and 3/3 replay. The agent receives no ground-truth label.

## 0:42–1:06 — engineering choices

Use the architecture slide. Explain only components with evidence:

- exact source excerpts compile into typed and hashed claims;
- benchmark labels are removed before system invocation;
- a data-only interpreter runs in a credential-minimized bounded worker;
- canonical-state memory and claim-progress priority direct search;
- `ACCEPT` requires complete finite exploration;
- `REJECT` requires shrinking plus triple replay; and
- every incomplete execution becomes `UNKNOWN`.

## 1:06–1:32 — final measured comparison

Show the 28 paired-case table:

- Replay: 0.500 balanced accuracy.
- FidelityGate: 1.000, with 14/14 clean specificity and 14/14 mutant recall.
- Four held-out mutation families: 1.000 across 8 cases.
- Every final witness: 3/3 replay.

Say explicitly: “This is synthetic benchmark evidence, not a production-performance estimate.”

## 1:32–1:52 — reviewer-usable evidence

Show `artifacts/envmutationbench/report.html`: every case, system comparison, suite and fixture hashes, exact source excerpt, forbidden state, minimal action sequence, and replay counts. The JSON evidence is the machine-verifiable source of truth.

## 1:52–2:13 — search ablation

Under the same 200-transition budget, BFS and random search miss the sparse mutant and return `UNKNOWN`; claim-directed search rejects in 30 transitions. The paired clean case remains `UNKNOWN`, proving the system does not convert search failure into acceptance.

## 2:13–2:34 — removed experiment

Show `artifacts/iterations/oracle-failure.json`.

“The first run scored 0.929 because the temporal oracle confused access before expiry with access after expiry. A second clean fixture remained open after its terminal reset. Both failures are preserved with a one-command reproducer.”

## 2:34–2:54 — hot take and reproducibility

“The hard part of agent evaluation is not generating more scenarios. It is falsifying the evaluator’s own assumptions. A score without a minimal replay and source-backed oracle is weak evidence.”

End on `bin/verify`: pinned setup, 32 tests, 92%+ coverage, benchmark-byte checks, and byte-identical committed evidence.

The checked-in video is 174.5 seconds. Captions are burned in and also committed as `demo/fidelitygate-demo.srt`.
