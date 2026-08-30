# Architecture

## End-to-end flow

```text
approved policy files
        |
        v
evidence compiler ---- hashes source + validates anchor/exact excerpt
        |
        v
typed forbidden-state claims             evaluator-only labels
        |                                        |
        +----------> unlabeled AuditCaseSpec <---+ (labels removed here)
                              |
                              v
                    resource-bounded worker
                              |
                    data-only workflow adapter
                              |
        +---------------------+---------------------+
        |                     |                     |
 execute action       coverage memory       check every claim
        |                     |                     |
        +---------- claim-directed frontier <------+
                              |
                 contradiction / exhaustion / bound
                    /              |             \
              shrink + replay   complete          incomplete
                    |              |                  |
                 REJECT          ACCEPT             UNKNOWN
                    |
          JSON + Markdown + HTML + product trajectory
```

## Agent loop

The falsification agent has a fixed instruction and a narrow tool vocabulary: reset, enumerate actions, execute, check claims, update coverage, prioritize frontier, shrink, replay, and emit a verdict. Its memory is the canonical-state archive plus frontier priority. The priority is the maximum number of forbidden-state clauses currently satisfied, with depth and discovery order as deterministic tie-breakers.

This is a deliberate non-LLM agent. The finite-state task has exact tools and a checkable oracle; adding a language model to the verdict path would increase uncertainty without adding capability. The agent is still autonomous: it chooses which state to inspect next, carries coverage forward, reacts to observations, invokes verification, and terminates under a three-way policy.

## Why each component exists

| Component | Structural reason | Evidence |
|---|---|---|
| Evidence compiler | A typed invariant without a source can encode the wrong rule confidently. | Forged excerpts, anchors, and path escapes fail tests; evidence hashes enter every report. |
| Label-isolation model | A benchmark system must not branch on ground truth or family. | `CaseSpec.audit_input()` removes labels; regression tests inspect the public fields. |
| Data-only workflow DSL | Synthetic fixtures should not execute arbitrary submitted code. | The DSL supports only typed comparisons/effects; a shell-shaped action-name test cannot create a file. |
| Resource-bounded worker | Evaluations need timeout/output/resource failure isolation and credential minimization. | Timeout, crash, and invalid-output tests all become `UNKNOWN`. |
| Expert replay baseline | Represents the acceptance process FidelityGate claims to improve. | 0.500 balanced accuracy across 28 paired cases. |
| Canonical-state archive | Avoids re-exploring equivalent environment states. | Complete clean graphs finish in bounded state/transition counts. |
| Claim-directed priority | Sparse unsafe paths can be buried behind irrelevant state. | Stress mutant: 30 transitions versus BFS/random `UNKNOWN` at 200. |
| Per-transition claims | Final state alone can erase ordering and transient violations. | The initial temporal-oracle failure forced explicit event semantics. |
| Shrinker | Reviewers need the smallest useful witness, not a search transcript. | Median witness length is 2; noisy-sequence regression removes irrelevant actions. |
| Triple replay | A flaky observation cannot justify rejection. | All primary witnesses replay 3/3; replay failure maps to `UNKNOWN`. |
| Three-way verdict | Failure to search, execute, validate, or replay is not evidence of fidelity. | Depth, state, transition, timeout, worker, and evidence failures fail closed. |
| Complete evaluator/reports | Improvement claims must be reproducible and include failures. | One command emits JSON, Markdown, HTML, per-case outcomes, hashes, and claim boundaries. |

## Trust boundaries

1. **Evidence boundary:** only files below `evidence/` are accepted; paths, anchors, and exact excerpts are checked.
2. **Benchmark boundary:** labels stay in the evaluator; systems receive `AuditCaseSpec` only.
3. **Execution boundary:** fixture data is interpreted by a code-free DSL in a disposable subprocess with a minimal environment and POSIX resource limits.
4. **Verdict boundary:** the adapter cannot return a verdict; the harness evaluates claims and replay.
5. **Action boundary:** all current actions are synthetic state transitions. There are no network, shell, filesystem, credential, or production-tool capabilities.
6. **Human boundary:** reports support a qualified reviewer and never execute a consequential approval.

The subprocess is not claimed to be a general hostile-code sandbox. Network denial is structural because the fixture language has no network or code-execution primitive. Supporting arbitrary Python adapters would require a stronger OS/container boundary and remains explicitly out of scope until that control exists.

## Prior-art influence

- Hypothesis informed stateful generation and counterexample shrinking.
- RESTler and Schemathesis informed schema-first action execution.
- AALpy informed explicit state-machine/conformance separation.
- MDPFuzz informed coverage memory and mutation-based evaluation.
- Go-Explore informed archive/frontier thinking, but its non-commercial reference code is not used.
- OPA/Witness informed source/decision provenance.
- Inspect AI informed trajectory and sandbox artifact expectations.

The implementation is original and uses none of those codebases as a runtime dependency.
