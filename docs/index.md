# Driftcut

**Early-stop decision gating for LLM model migrations.**

Cut bad migration candidates before they burn budget on full-scale evaluations.

---

## What is Driftcut?

Driftcut is a CLI tool that helps teams decide quickly whether a model migration is worth pursuing. Instead of running your full prompt corpus against a candidate model, Driftcut samples strategically, evaluates progressively, and tells you early: **stop now**, **keep sampling**, or **proceed to full evaluation**.

## The problem it solves

When a team wants to switch from one LLM to another — for cost, latency, privacy, or quality — the evaluation process is wasteful:

1. Pick a candidate model
2. Run the entire test corpus (hundreds or thousands of API calls)
3. Wait hours for results
4. Discover at the end that the candidate breaks critical categories
5. Start over with another candidate

Driftcut answers a simpler question first:

> "Should we continue this migration, or are we already seeing enough risk to stop?"

## Quick links

- [Getting Started](getting-started.md) — Install and run your first migration test
- [Configuration](configuration.md) — Full YAML config reference
- [Concept](concept.md) — Design philosophy and how the decision engine works
- [Roadmap](roadmap.md) — What's built, what's next

## Current status

!!! warning "Pre-release"
    Driftcut is in active development. The `validate` and `run` commands work today. The decision engine and reports are coming next.

```bash
pip install driftcut          # coming soon — install from source for now
driftcut validate --config migration.yaml
driftcut run --config migration.yaml
```
