# Evaluation contract

## Primary metric

Balanced accuracy over environment packages labeled `clean` or `mutated`:

```text
balanced_accuracy = (clean_specificity + mutant_recall) / 2
```

`ACCEPT` is the positive prediction for clean cases and `REJECT` for mutated cases. `UNKNOWN` is counted as incorrect for the case's class in the primary metric. This preserves the safety value of abstention without making abstention a scoring exploit.

## Good final result, defined before evaluation

The advanced solution should:

- improve balanced accuracy over every declared baseline on the same held-out cases;
- preserve high clean specificity rather than rejecting everything;
- produce a deterministically replayable witness for every deterministic rejection;
- localize the violated source-backed claim and relevant transition;
- reduce qualified-reviewer time without hiding uncertainty;
- show the improvement survives held-out mutation families and clean near-misses.

No general performance claim will be made from the two-case smoke suite.

## Secondary metrics

- mutant recall, including critical-mutation recall;
- clean specificity and false-positive rate;
- mutation kill rate by family;
- replay success rate;
- median minimized witness length;
- source/claim localization accuracy;
- risk-weighted claim coverage;
- states, transitions, and tools explored;
- human review time per case;
- runtime and model cost per case.

## Fairness

Every system receives the same suite manifest, adapter, expert traces, evidence, claim set, and ground-truth-hidden execution interface. Resource differences are recorded. Search methods may use their declared action budgets; a budget-matched random baseline isolates the value of directed exploration.

## Smoke cases

1. `refund_clean`: high-value refunds require manager approval; all declared behavior is consistent.
2. `refund_admin_bypass`: an admin can issue a high-value refund without manager approval; the same expert traces still pass.

The expert traces include an approved high-value refund and an unapproved low-value refund. They intentionally do not exercise the admin bypass. The challenging case is therefore the mutant: it establishes why replay-only acceptance is insufficient.

## EnvMutationBench case design

At least 10 cases will cover authorization, identity, reward, tool preconditions, time/order, stale state, evidence contradiction, hidden effects, partial observations, retries, stochastic behavior, and memory contamination. Each case includes:

- paired clean and defective packages where possible;
- source-backed or explicitly synthetic claims;
- expert traces;
- defect provenance and minimal trigger held outside system prompts;
- reviewer-confirmed label;
- expected detector class;
- deterministic seed or stochastic replay schedule.

## Artifact schema

Each run records suite path and SHA-256, system name, limits, per-case verdict, prediction, witness, explored sequences, replay outcome, confusion counts, and aggregate metrics. Failures remain in the complete output.
