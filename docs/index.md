# Driftcut

**Early-stop decision gating for LLM model migrations.**

Alpha CLI for sampling migration candidates before you commit to a full evaluation.

---

## What is Driftcut?

Driftcut is a CLI tool for the step before a full migration evaluation. Instead of immediately running your whole prompt corpus against a candidate model, Driftcut samples strategically, runs baseline and candidate models on representative batches, and gives you latency and cost signals early.

The quality layer that enables automatic **stop now**, **keep sampling**, or **proceed to full evaluation** decisions is planned next.

## The problem it solves

When a team wants to switch from one LLM to another - for cost, latency, privacy, or quality - the evaluation process is wasteful:

1. Pick a candidate model
2. Run the entire test corpus (hundreds or thousands of API calls)
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
    Driftcut is in active development. The `validate` and `run` commands work today. The decision engine, failure archetypes, and HTML reporting are coming next.

### What works today

- Config and corpus validation
- Stratified sampling by category and criticality
- Concurrent baseline/candidate execution via LiteLLM
- Latency and cost tracking
- JSON results export

### What comes next

- Deterministic quality checks
- Judge-based comparison
- Failure archetype classification
- Stop / continue / proceed decisions
- Richer reports

```bash
pip install driftcut          # coming soon - install from source for now
driftcut validate --config migration.yaml
driftcut run --config migration.yaml
```
