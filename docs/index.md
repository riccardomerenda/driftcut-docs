# Driftcut

**Early-stop decision gating for LLM model migrations.**

v0.9.0 alpha CLI for sampling migration candidates before you commit to a full evaluation.

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
- [CLI Reference](cli-reference.md) - Commands, flags, and examples
- [Concept](concept.md) - Design philosophy and planned architecture
- [Roadmap](roadmap.md) - What's built and what's next

## Current status

!!! warning "Pre-release"
    Driftcut is in active development. The current alpha ships `driftcut init` scaffolding, deterministic checks, tiered judge escalation for ambiguous prompts, historical replay, richer failure archetype summaries, per-category scorecards, and `STOP` / `CONTINUE` / `PROCEED` decisions.

### What works today

- Config and corpus validation
- Stratified sampling by category and criticality
- Concurrent baseline/candidate execution via LiteLLM
- Transient retry handling for rate limits, timeouts, connection failures, and 5xxs
- Historical replay on canonical paired-output JSON
- Deterministic checks for format, JSON validity, required content, and output length limits
- Tiered judging with light-to-heavy escalation for ambiguous prompts
- Latency tracking plus baseline, candidate, and judge cost tracking
- Optional Redis memory for baseline caching and run-history persistence
- `STOP` / `CONTINUE` / `PROCEED` decisions during the run
- JSON results export
- HTML report generation
- Per-category quality scorecards in JSON and HTML output
- Richer semantic failure archetypes such as `refusal_regression`, `instruction_miss`, and `incomplete_answer`
- `driftcut init` scaffolding for instant project setup

### What comes next

- More polished reports and benchmark demos

## See the output

The fastest way to understand Driftcut is to look at the artifacts it produces.

### Terminal summary

```text
$ driftcut run --config migration.yaml

GPT-4o to Claude Haiku migration gate
  Mode:      live
  Baseline:  openai/gpt-4o
  Candidate: anthropic/claude-haiku

  Batch 1: 12 prompts, 0 API errors, $0.1840 cumulative
    Decision: CONTINUE (58% confidence)
    Judge coverage: 3/3 ambiguous prompts
    Risk is still borderline after the first sampled batch.

  Batch 2: 12 prompts, 0 API errors, $0.3120 cumulative
    Decision: PROCEED (82% confidence)
    Judge coverage: 4/4 ambiguous prompts
    Risk stayed below the configured proceed threshold.

Run complete
  Prompts tested: 24/30
  Batches tested: 2
  Total cost:     $0.3120
  Judge cost:     $0.0280
  Latency p50:    910ms (baseline) -> 690ms (candidate)
  Latency p95:    1480ms (baseline) -> 1100ms (candidate)
  Decision:       PROCEED (82% confidence)
  Reason:         Risk stayed below the configured proceed threshold.
  Top category:   extraction (11% risk | json_invalid x2)
```

### `results.json` excerpt

```json
{
  "mode": "live",
  "decision": {
    "outcome": "PROCEED",
    "confidence": 0.82,
    "reason": "Risk stayed below the configured proceed threshold."
  },
  "decision_history": [
    {
      "outcome": "PROCEED",
      "metrics": {
        "category_scores": [
          {
            "category": "extraction",
            "overall_risk": 0.11,
            "archetypes": {
              "json_invalid": 2
            }
          }
        ]
      }
    }
  ],
  "cost": {
    "baseline_usd": 0.184,
    "candidate_usd": 0.1,
    "judge_usd": 0.028,
    "total_usd": 0.312
  },
  "batches": [
    {
      "batch_number": 1,
      "results": [
        {
          "prompt_id": "cx-001",
          "candidate": {
            "latency_ms": 640.0,
            "retry_count": 1,
            "cost_usd": 0.009,
            "error": null
          }
        }
      ]
    }
  ]
}
```

You also get an HTML report with the same decision, threshold context, latency/cost summary, failure archetypes, and prompt examples.

```bash
pip install driftcut
driftcut init
driftcut validate --config migration.yaml
driftcut run --config migration.yaml
driftcut replay --config replay.yaml --input replay.json
```
