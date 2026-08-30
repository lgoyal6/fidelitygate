# Coding-agent trajectory capture

## Raw source

Codex CLI stores session records as append-only JSONL below:

```text
${CODEX_HOME:-$HOME/.codex}/sessions/YYYY/MM/DD/rollout-*.jsonl
```

The active build thread is identifiable through `CODEX_THREAD_ID`. Raw logs can contain private context and remain outside Git under `trajectories/raw/` or the Codex home directory.

## Export

Export a redacted, judge-readable trace by thread ID:

```bash
uv run python scripts/export_codex_trajectory.py \
  --thread-id "$CODEX_THREAD_ID" \
  --output trajectories/build-thread.jsonl \
  --ordinal-range 1600:1900
```

Or pass an explicit session file:

```bash
uv run python scripts/export_codex_trajectory.py \
  --input /absolute/path/to/rollout.jsonl \
  --output trajectories/build-thread.jsonl
```

The exporter keeps user/assistant messages, tool calls, and tool responses; excludes system/developer instructions and internal reasoning; recursively redacts common credential and device-code patterns; and writes an adjacent manifest with source hash, counts, ordinal selection, and export policy. Repeated inclusive `--ordinal-range START:END` flags create bounded representative slices. Review the result manually before committing it.

## Submission trajectory set

The committed coding-agent set covers:

1. `coding-agent/01-problem-selection.jsonl` — micro1 research, prior-art kills, and the EnvTruth-to-FidelityGate narrowing;
2. `coding-agent/02-architecture-plan.jsonl` — rubric grading, internal-equivalent defense, architecture research, and approved plan;
3. `coding-agent/03-harness-baseline.jsonl` — repository creation, trace capture, baseline, and first causal vertical slice;
4. `coding-agent/04-benchmark-iterations.jsonl` — 28-case expansion, evaluator failures, fixes, search ablation, and controls;
5. `coding-agent/05-verification-demo.jsonl` — full verification, clean clone, video production, and publishing checkpoint.

Each JSONL has an adjacent manifest with source/output hashes and record counts. The exports were JSON-parsed and searched for raw home paths, common token formats, bearer headers, and the one-time device code. The exporter is data minimization, not a guarantee that every possible secret format has been removed.

## Product-agent trajectories

The falsification agent has its own stable, machine-readable trajectory schema. These committed examples contain the public agent instruction, ordered tool events, observations, coverage updates, verification, and final outcome:

- `trajectories/product-agent/env_001b.json` — normal approval-bypass case;
- `trajectories/product-agent/env_900b-guided.json` — combinatorial stress case where frontier priority changes the result.

Generate either with `fidelitygate trace`. Product trajectories never contain benchmark labels because the agent receives `AuditCaseSpec`, not `CaseSpec`.
