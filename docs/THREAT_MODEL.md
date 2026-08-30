# Threat model

## Assets

- correctness and provenance of the acceptance verdict;
- confidentiality of source data, credentials, and trajectories;
- integrity of suite labels and benchmark results;
- reproducibility of counterexamples;
- safety of the host running untrusted adapters.

## Adversaries and failures

- a defective environment that returns plausible observations while hiding side effects;
- a malformed fixture that attempts schema confusion, state explosion, path escape, or resource exhaustion;
- a mutation generator that leaks labels through names or syntax;
- a semantic model that invents actions, claims, or citations;
- a benchmark author who overfits detectors to known mutation templates;
- accidental false acceptance caused by omitted actions, incomplete evidence, or flaky replay.

## Controls

- compute verdicts outside the adapter;
- interpret only the typed data DSL; it has no code, network, shell, filesystem, or credential primitive;
- run the interpreter in a disposable subprocess with a minimal environment and POSIX limits;
- hash suites, adapters, sources, and reports;
- split mutation generation, label review, and evaluation;
- validate action schemas and normalize events;
- enforce bounds and convert incompleteness to `UNKNOWN`;
- require deterministic replay for deterministic rejection;
- include clean near-misses and held-out mutation families;
- require human approval in consequential domains;
- redact trajectory exports and keep raw logs outside Git.

## Current limitations

The final CLI runs the data-only adapter in a subprocess with CPU, file-size, file-descriptor, timeout, and Linux address-space limits. Crash, timeout, oversized output, or invalid output becomes `UNKNOWN`. The worker does not inherit application credentials.

This is defense in depth for a code-free interpreter, not a general hostile-code sandbox. The process still runs with the user's OS identity and the host does not enforce a network namespace on macOS. Arbitrary Python, shell, package installation, and production tool adapters are therefore rejected by design.

Suite ground truth is present in evaluator files but removed before system invocation. Opaque fixture IDs reduce accidental leakage; they do not make a public synthetic benchmark secret. Family-level holdout reduces iterative overfitting but is not independent validation.
