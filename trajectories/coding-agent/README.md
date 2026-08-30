# Coding-agent trajectory index

These are bounded, judge-readable slices of the append-only Codex build session. They preserve the user/assistant messages, tool calls, and tool responses needed to follow each decision while excluding developer/system instructions, private reasoning, runtime metadata, and raw local logs.

| File | What it demonstrates |
|---|---|
| `01-problem-selection.jsonl` | micro1 product/evaluation research, prior-art kills, and the EnvTruth-to-FidelityGate narrowing |
| `02-architecture-plan.jsonl` | rubric pressure test, internal-equivalent defense, reusable algorithms, and the approved plan |
| `03-harness-baseline.jsonl` | trace preflight, repository creation, baseline, and first causal vertical slice |
| `04-benchmark-iterations.jsonl` | 28-case expansion, exposed evaluator failures, fixes, search ablation, and safety controls |
| `05-verification-demo.jsonl` | repository gates, clean clone, demo production, visual verification, and publishing checkpoint |

Each JSONL record retains its original timestamp and ordinal. Each adjacent manifest records the raw-session hash at export time, selected inclusive ordinal ranges, source/export counts, output hash, and redaction policy. The final slice omits a diagnostic interval whose terminal output echoed a role index; this prevents excluded instruction records from re-entering indirectly through tool output.

Before commit, every file was parsed with `jq` and searched for raw home paths, common API/GitHub token formats, bearer credentials, generic secret assignments, and the GitHub one-time device code. Raw session logs remain outside Git. These checks reduce exposure risk; they are not a mathematical guarantee against every possible secret format.
