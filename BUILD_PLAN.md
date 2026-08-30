# FidelityGate build plan

This plan optimizes for evidence quality, engineering rigor, and rubric score. It has no timing-based scope cuts. Each component must earn its place with a measured improvement or be removed and documented as a negative result.

## Product contract

**User:** an environment engineer or domain expert deciding whether an agent/RL environment faithfully implements source-backed operational rules.

**Bottleneck:** expert demonstrations and reward checks cover intended paths, but they do not reveal reachable shortcuts, contradictory tool behavior, reward-policy divergence, or missing evidence. Manual adversarial review is difficult to repeat and hard to compare between reviewers.

**Outcome:** a reproducible acceptance report containing a bounded verdict, cited claim coverage, concrete minimized counterexamples, deterministic replay bundles, and explicit uncertainty. A qualified human makes the final consequential decision.

**Primary metric:** balanced accuracy on clean versus independently seeded defective environments. `UNKNOWN` counts as incorrect for the primary metric, preventing abstention from inflating the score.

## Stage 0 — Provenance and trajectory capture

- Label pre-existing versus hackathon-created assets.
- Capture coding-agent instructions, tool calls, responses, retries, feedback, and checkpoints.
- Export redacted, representative trajectories while keeping raw session logs outside Git.
- Maintain third-party notices and a dependency/license ledger.

**Gate:** a judge can trace representative implementation decisions from instruction through verified artifact without receiving secrets or unrelated private context.

## Stage 1 — Evaluation contract before advanced implementation

- Freeze the verdict model: `ACCEPT`, `REJECT`, `UNKNOWN`.
- Freeze balanced accuracy and secondary metrics.
- Define the same cases, evidence, resource limits, and output schema for baseline and final system.
- Define failure policy: invalid adapters, incomplete exploration, unavailable evidence, or failed replay cannot silently become acceptance.

**Gate:** metric code has unit tests using hand-calculated confusion matrices and abstentions.

## Stage 2 — Harness-first benchmark runner

- One command runs a versioned suite against a named system.
- Emit machine-readable JSON and a concise comparison table.
- Record suite hash, implementation version, seed, explored state count, action count, and result evidence.
- Make artifacts deterministic except for declared timing metadata.

**Gate:** a clean checkout reproduces a byte-stable semantic result for the smoke suite.

## Stage 3 — EnvMutationBench

Build at least 10 public or synthetic cases before making general claims. Grow toward a matrix of clean/mutated pairs across:

1. authorization bypass;
2. identity/role confusion;
3. reward-policy mismatch;
4. tool precondition violation;
5. temporal ordering violation;
6. stale or inconsistent state;
7. evidence/source contradiction;
8. hidden side effects;
9. partial observability or omitted fields;
10. error-path and retry divergence;
11. stochastic inconsistency;
12. cross-episode memory contamination.

Every mutant must have a provenance record, minimal triggering condition, expected detector class, and clean paired environment. Keep a held-out mutation family for generalization testing.

**Gate:** independent mutation review confirms defects are real, nontrivial, and absent from clean pairs.

## Stage 4 — Evidence compiler

- Ingest policy text, schemas, tables, and approved source material.
- Compile source-backed claims into typed preconditions, postconditions, invariants, and temporal obligations.
- Preserve claim-to-source spans and distinguish machine-checkable, human-reviewed, and unsupported claims.
- Require human approval for consequential claim compilation.

**Gate:** every executable claim has a source pointer or is explicitly labeled synthetic; unsupported assertions never become silent ground truth.

## Stage 5 — Environment adapter SDK

Define a narrow contract:

- reset/clone state;
- enumerate or propose actions;
- validate and execute an action;
- expose safe observations and normalized events;
- evaluate claims;
- serialize a replay bundle;
- declare determinism and stochastic controls.

Add conformance tests, schema validation, capability declarations, and adapter version hashes.

**Gate:** an intentionally malicious or malformed adapter cannot forge a successful report merely by returning a truthy value.

## Stage 6 — Sandboxed execution

- Run untrusted adapters in disposable isolated workers.
- Deny network and credentials by default.
- Enforce CPU, memory, state, depth, action, output, and wall-clock bounds.
- Make consequential tools simulated and require explicit approval gates.

**Gate:** tests demonstrate blocked network access, contained filesystem writes, timeout handling, and artifact-only egress.

## Stage 7 — Deterministic falsification kernel

- Exhaustive bounded breadth-first search for finite action spaces.
- Check invariants after every transition, not just terminal reward.
- Deduplicate canonical states while retaining alternative paths where history matters.
- Return shortest-by-depth contradictions first.

**Gate:** mutation tests show each search and claim-checking branch is causally necessary.

## Stage 8 — Shrinking and replay

- Delta-debug action sequences and simplify parameters.
- Replay witnesses from a clean reset multiple times.
- Package initial state, actions, observations, normalized events, claim, source, and observed/expected values.
- Reject flaky witnesses; report stochastic uncertainty separately.

**Gate:** every deterministic `REJECT` has a one-command replay and a minimality claim bounded to the shrink strategy.

## Stage 9 — Coverage-guided and archive-based exploration

Add these only if benchmark evidence shows deterministic BFS cannot scale:

- transition/claim/state-feature coverage guidance inspired by coverage-guided fuzzing;
- novelty archives and return-to-promising-state search inspired by Go-Explore methodology, implemented independently;
- rare-event and boundary-value action mutation;
- active automata learning for partially documented transition systems.

**Gate:** controlled ablation improves held-out mutant recall or reduces cost at fixed recall. Otherwise remove it.

## Stage 10 — Symbolic and stochastic analysis

- Optional symbolic constraint solving for numerical and role boundaries.
- Statistical replay with fixed seed schedules and confidence intervals for stochastic environments.
- Sequential tests for claimed probabilities and bounded nondeterminism.
- Metamorphic relations when a single oracle is unavailable.

**Gate:** claims distinguish exhaustive proof within a finite abstraction, statistical evidence, and heuristic search.

## Stage 11 — Semantic adversary

Use an LLM only for tasks not reliably expressible as deterministic code:

- propose adversarial plans from source claims and tool schemas;
- identify likely ambiguity or missing evidence;
- map natural-language source clauses to candidate typed checks;
- explain an already verified witness.

The model cannot issue the verdict. Every proposed witness must execute and every explanation must cite the recorded trace.

**Gate:** hallucinated actions and unsupported claims are rejected by schema and provenance checks; ablation demonstrates incremental recall.

## Stage 12 — Independent mutation pipeline

- Generate mutations without showing their labels to the system under test.
- Separate mutation authorship from evaluation execution.
- Use semantic mutation operators plus manually authored defects.
- Detect trivial lexical leakage and duplicate variants.
- Add clean near-misses so anomaly detection alone cannot win.

**Gate:** held-out families and independent review show the system is finding behavioral contradictions rather than recognizing mutant fingerprints.

## Stage 13 — Verdict and provenance engine

- Compute coverage of reachable states, claims, tools, roles, sources, and mutation families.
- `ACCEPT` only when all required checks complete over the declared bound.
- `REJECT` only on a replayable contradiction.
- Return `UNKNOWN` with structured missing evidence, incomplete bounds, or instability reasons.
- Sign/hash reports and evidence bundles.

**Gate:** no failure-to-run path is representable as acceptance.

## Stage 14 — Fair baselines, ablations, and negative results

Baselines:

1. expert-trajectory replay;
2. bounded deterministic random exploration with the same transition budget;
3. breadth-first falsification without claim-directed priority;
4. the final claim-directed falsification agent.

Ablate evidence grounding, per-transition checks, shrinking, coverage guidance, archive search, symbolic boundaries, semantic adversary, and replay verification individually.

**Gate:** the changelog keeps only components with measured benefit and includes removed experiments with lessons.

## Stage 15 — Reproducibility, security, and CI

- Pin dependencies and publish exact clean-environment commands.
- Run format, lint, type, unit, integration, mutation, replay, and benchmark checks in CI.
- Produce fixtures with public/synthetic data only.
- Include approximate runtime and model cost by suite.
- Verify from a clean clone without private credentials.

**Gate:** a separate clean directory reproduces baseline, final, and comparison artifacts.

## Stage 16 — Human-quality product finish

- Evidence-first report with an executive summary, decision boundary, claim coverage, and expandable replay.
- No generic chat UI and no unsupported prose.
- Five-minute demonstration begins with the problem and replay baseline, runs one environment end to end, shows the main measured improvement, and includes one removed experiment.
- Close the changelog with the main failure mode and a practical hot take.

**Gate:** a domain reviewer can understand and sign the artifact without reading source code, while an engineer can reproduce every material claim.

## Implemented status

Stages 0–8 and 12–16 are implemented for the data-only fixture contract: trajectory export, evidence/metric contracts, one-command harness, 14-pair EnvMutationBench, evidence compilation, adapter DSL, resource-bounded worker, deterministic and claim-directed search, shrinking/triple replay, mutation provenance, three-way verdicts, baselines/ablations, CI, reproduction, and evidence-first HTML output.

Stage 9 is implemented only for claim-directed coverage priority. Archive return and active automata learning were not added because no retained benchmark establishes incremental value. Stage 10 symbolic/stochastic analysis is not claimed; every committed fixture is deterministic and finite. Stage 11's LLM semantic adversary was rejected for the verdict path because the current claims are already typed. Arbitrary-code adapters remain blocked until a true hostile-code sandbox exists.

The build closes with 28 primary cases, 8 family-holdout cases, a combinatorial stress ablation, a reproducible negative oracle result, over 90% test coverage, committed product-agent trajectories, and byte-reproducible evidence artifacts.
