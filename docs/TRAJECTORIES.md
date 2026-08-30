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
  --output trajectories/build-thread.jsonl
```

Or pass an explicit session file:

```bash
uv run python scripts/export_codex_trajectory.py \
  --input /absolute/path/to/rollout.jsonl \
  --output trajectories/build-thread.jsonl
```

The exporter keeps user/assistant messages, tool calls, and tool responses; excludes system/developer instructions and internal reasoning; recursively redacts common credential patterns; and writes an adjacent manifest with source hash, counts, and export policy. Review the result manually before committing it.

## Submission trajectory set

Representative trajectories will cover:

1. problem selection and prior-art kill reasoning;
2. harness and baseline implementation;
3. counterexample exploration and shrinker development;
4. a failed/removed experiment and the evidence that removed it;
5. final clean-clone reproduction and human checkpoint.

Every trace must remain understandable from instruction through tool response and verified artifact. The exporter is data minimization, not a guarantee that every possible secret format has been removed.

## Product-agent trajectories

The falsification agent has its own stable, machine-readable trajectory schema. These committed examples contain the public agent instruction, ordered tool events, observations, coverage updates, verification, and final outcome:

- `trajectories/product-agent/env_001b.json` — normal approval-bypass case;
- `trajectories/product-agent/env_900b-guided.json` — combinatorial stress case where frontier priority changes the result.

Generate either with `fidelitygate trace`. Product trajectories never contain benchmark labels because the agent receives `AuditCaseSpec`, not `CaseSpec`.
