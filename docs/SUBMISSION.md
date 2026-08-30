# Submission copy

## Title

FidelityGate — falsify an agent environment before you trust its eval

## One-line description

An evidence-bounded agent that finds, minimizes, and replays policy-violating shortcuts in expert-built agent and RL environments.

## Intended user

Environment engineers and domain experts approving operational simulations for agent training or evaluation.

## Bottleneck

Expert happy paths can all pass while a reachable tool sequence violates the approved policy. Manual adversarial review is inconsistent, difficult to reproduce, and rarely produces a minimal source-cited witness.

## Solution

FidelityGate compiles exact policy excerpts into typed claims, strips benchmark labels, explores the environment with claim-directed coverage memory, checks every transition, minimizes contradictions, and requires identical triple replay. It accepts only complete finite exploration, rejects only replayable evidence, and otherwise returns `UNKNOWN`.

## Demonstrated improvement

Across 28 paired synthetic cases, expert-trajectory replay scores 0.500 balanced accuracy because it accepts every seeded defect. FidelityGate scores 1.000 with 14/14 clean specificity, 14/14 mutant recall, and 3/3 replay for every witness. On a fixed 200-transition stress case, claim-directed search detects a sparse mutant in 30 transitions while BFS and random search return `UNKNOWN`.

## Main failure mode

An incorrect oracle can make a strong searcher confidently wrong. The first run reproduced a temporal false positive and incomplete terminal model; both remain in the changelog and negative-result artifact.

## Hot take

The reliability moat for agent environments is not another average task-success leaderboard. It is versioned falsification evidence: the smallest source-contradicting behavior the environment permits, replayable by a skeptical reviewer.

## Disclosure

- Coding agent: Codex CLI.
- Product agent: deterministic FidelityGate falsification agent.
- Data: public repository code plus synthetic policies and fixtures only.
- Model calls/cost: none / $0.
- Consequential actions: none; all transitions are simulated and a human remains the decision-maker.
- Claim boundary: synthetic benchmark performance is not production validation.
