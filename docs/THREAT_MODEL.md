# Threat model

## Assets

- correctness and provenance of the acceptance verdict;
- confidentiality of source data, credentials, and trajectories;
- integrity of suite labels and benchmark results;
- reproducibility of counterexamples;
- safety of the host running untrusted adapters.

## Adversaries and failures

- a defective environment that returns plausible observations while hiding side effects;
- an adapter that forges coverage, blocks reset, exfiltrates data, or consumes unbounded resources;
- a mutation generator that leaks labels through names or syntax;
- a semantic model that invents actions, claims, or citations;
- a benchmark author who overfits detectors to known mutation templates;
- accidental false acceptance caused by omitted actions, incomplete evidence, or flaky replay.

## Controls

- compute verdicts outside the adapter;
- isolate arbitrary adapters and deny network/credentials;
- hash suites, adapters, sources, and reports;
- split mutation generation, label review, and evaluation;
- validate action schemas and normalize events;
- enforce bounds and convert incompleteness to `UNKNOWN`;
- require deterministic replay for deterministic rejection;
- include clean near-misses and held-out mutation families;
- require human approval in consequential domains;
- redact trajectory exports and keep raw logs outside Git.

## Current smoke limitations

The synthetic refund adapter runs in process because it is repository-owned, deterministic, and has no I/O capabilities. This does not establish safe execution of third-party environments. The CLI is a research harness, not a production security boundary.
