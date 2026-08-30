# Architecture

## Decision flow

```text
source-backed claims --------> typed claim set
                                  |
suite manifest -> adapter -> sandboxed execution -> observations/events
                         |             |
                  baseline replay      +-> bounded explorer
                                             |
                                      claim contradiction?
                                        /            \
                                      no              yes
                                      |                |
                            coverage complete?     shrink + replay
                               /       \               |
                             yes        no          REJECT + witness
                              |          |
                            ACCEPT     UNKNOWN
```

The current smoke slice implements the manifest, synthetic adapter, replay baseline, deterministic explorer, claim checker, shrinker, replay verifier, evaluator, and report. Sandboxing and source-text compilation are explicit later stages, not decorative placeholders disguised as implemented features.

## Why each current component exists

| Component | Structural reason |
|---|---|
| Suite manifest | Makes baseline and final receive identical cases and freezes ground truth outside either system. |
| Adapter contract | Separates exploration and evaluation logic from a particular environment. |
| Replay baseline | Models the common validation process the product claims to improve. |
| Breadth-first explorer | Completes a finite declared bound and naturally finds shortest-depth failures. |
| Per-transition claim checks | Detects violations that a terminal reward or final state can hide. |
| Shrinker | Turns a failure into a reviewer-usable counterexample instead of a noisy trace. |
| Replay verification | Prevents flaky or non-reproducible behavior from becoming a confident rejection. |
| Three-way verdict | Prevents missing evidence or incomplete search from becoming false acceptance. |
| Evaluator | Connects every improvement claim to the same benchmark and metric. |

## Trust boundaries

The suite labels and claim definitions are benchmark inputs. An adapter controls state transitions but does not control verdict computation. The explorer treats observations as untrusted values and evaluates claims in the harness. Future arbitrary adapters move across a sandbox boundary. Reports never trigger external actions.

## Advanced architecture criterion

Advanced exploration is introduced only when the deterministic kernel establishes a failing benchmark frontier. Coverage guidance, active automata learning, symbolic reasoning, stochastic testing, and a semantic adversary are separate strategies behind the same adapter and result contracts. That allows one-variable ablations and prevents component count from masquerading as sophistication.
