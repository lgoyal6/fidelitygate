# Prior art and differentiation

Prior art is a first filter. FidelityGate survives only if it occupies a specific gap: source-grounded acceptance testing of complete agent environments, with behavioral mutants, bounded three-way verdicts, and minimized replayable contradictions.

| Project/category | What it already solves | Remaining gap relevant here | License posture |
|---|---|---|---|
| Inspect AI | Agent evaluation tasks, solvers, tools, sandboxes, logs | Infrastructure, not a source-claim fidelity acceptance gate or environment mutation benchmark | MIT; possible future integration |
| tau2-bench and similar tool-agent benchmarks | Multi-turn tool use against simulated domains | Measures agent success; does not validate whether the simulator itself faithfully enforces source rules | MIT; use benchmark patterns only |
| AgentDojo/ToolSandbox-style safety benches | Attacks, tool behavior, and safety evaluation | Focuses agent security/performance rather than accepting an expert-built environment as an artifact | Review per-project terms; no dependency now |
| Hypothesis | Property-based generation, stateful testing, shrinking | Requires a property and system model; lacks source provenance, environment verdicts, and mutation corpus | MPL-2.0; design patterns, evaluate dependency later |
| RESTler/Schemathesis | Stateful API schema fuzzing | API contract focus, not agent environment claims/rewards/trajectories | MIT; useful exploration patterns |
| AALpy | Active automata learning and conformance testing | Learns transition behavior but does not connect it to policy sources or human review artifacts | MIT; candidate strategy |
| OPA/Witness | Policy evaluation and decision provenance | Requires encoded policy and does not explore an agent environment for bypass sequences | Apache-2.0; candidate oracle/provenance integration |
| Z3/CrossHair | Symbolic constraint and contract analysis | Code/constraint focus; cannot alone test tool semantics or evidence fidelity | MIT-dominant; candidate bounded strategy |
| MDPFuzz | Coverage-guided fuzzing for RL policies | Tests policies, not whether a training/eval environment implements expert rules | MIT; methodology candidate |
| SWE-Mutation/SWE-ABS | Mutation-based evaluation of coding agents | Software issue/test domain, not operational agent environments | MIT; benchmark methodology candidate |
| Go-Explore | Archive and return exploration | General exploration algorithm with no source claims or verdict product | Reference code is non-commercial-only; method only, independent implementation |

## Explicitly rejected dependencies

- EvoMaster (LGPL), Storm (GPL), and PM4Py (AGPL): possible architectural inspiration, not acceptable embedded dependencies for this submission without a separate legal decision.
- WONDERBREAD and some benchmark corpora: non-commercial or custom restrictions conflict with a clean reusable stack.
- Go-Explore reference code: license prevents using it as a normal open-source building block here.

## Novelty risk

The product can collapse into “property-based testing with an LLM wrapper.” The defense must be empirical and structural:

1. claims retain source provenance and uncertainty;
2. the artifact under test is the entire environment, not the policy-playing agent;
3. the benchmark mutates environment semantics across tools, rewards, time, identity, and evidence;
4. counterexamples are minimized and replayable;
5. acceptance is bounded and missing coverage becomes `UNKNOWN`;
6. the system is evaluated on hidden mutation families and clean near-misses.

If those distinctions are not implemented and measured, the idea should be considered killed by prior art.
