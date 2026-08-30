# Security policy

## Scope

FidelityGate executes environment adapters and explores action sequences. Treat every submitted adapter, fixture, document, tool response, and trajectory as untrusted input.

The current smoke adapter is an in-process synthetic fixture with no network, subprocess, filesystem-write, credential, or external-action capability. Production adapters must run in a disposable sandbox with deny-by-default network access, bounded CPU and memory, an ephemeral filesystem, and explicit artifact export.

## Safety rules

- Never place credentials, private data, or raw session logs in the repository.
- Never let an evaluated environment call consequential production tools.
- Require a qualified human to approve any consequential decision.
- Validate manifests and action arguments before execution.
- Cap depth, actions, states, runtime, memory, and output size.
- Record hashes for suites, adapters, evidence, and reports.
- Treat adapter output as evidence, not trusted instructions.

Report security issues privately to the repository owner. Do not include sensitive exploit material in a public issue.
