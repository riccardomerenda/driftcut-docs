# Driftcut

**Early-stop decision gating for LLM model migrations.**

v0.4.0 alpha CLI for sampling migration candidates before you commit to a full evaluation.

---

## What is Driftcut?

Driftcut is a CLI for the step before a full migration evaluation. Instead of immediately running your whole prompt corpus against a candidate model, Driftcut samples strategically, runs baseline and candidate models on representative batches, checks deterministic quality signals, sends ambiguous prompts to a judge model, and gives you an early migration decision.

## The problem it solves

When a team wants to switch from one LLM to another for cost, latency, privacy, or quality, the evaluation process is wasteful:

1. Pick a candidate model
2. Run the entire test corpus
3. Wait hours for results
4. Discover at the end that the candidate breaks critical categories
5. Start over with another candidate

Driftcut answers a simpler question first:

> "Should we continue this migration, or are we already seeing enough risk to stop?"

## Quick links

- [Getting Started](getting-started.md) - Install and run your first migration test
- [Configuration](configuration.md) - Full YAML config reference
- [Concept](concept.md) - Design philosophy and planned architecture
- [Roadmap](roadmap.md) - What's built and what's next

## Current status

!!! warning "Pre-release"
    Driftcut is in active development. The current alpha already ships deterministic checks, judge-based comparison for ambiguous prompts, failure archetype summaries, and `STOP` / `CONTINUE` / `PROCEED` decisions.

### What works today

- Config and corpus validation
- Stratified sampling by category and criticality
- Concurrent baseline/candidate execution via LiteLLM
- Deterministic checks for format, JSON validity, required content, and output length limits
- Judge-based comparison for ambiguous prompts
- Latency tracking plus baseline, candidate, and judge cost tracking
- `STOP` / `CONTINUE` / `PROCEED` decisions during the run
- JSON results export
- HTML report generation

### What comes next

- Real light-to-heavy escalation for judge calls
- Richer failure archetypes beyond deterministic checks and `judge_worse`
- More polished reports and benchmark demos

```bash
pip install driftcut          # coming soon - install from source for now
driftcut validate --config migration.yaml
driftcut run --config migration.yaml
```
