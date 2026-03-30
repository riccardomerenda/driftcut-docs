# Concept

!!! info "Design document"
    This page describes Driftcut's design philosophy and planned architecture. Features marked with :white_check_mark: are implemented; others are under development. See the [Roadmap](roadmap.md) for current status.

## Core insight

Driftcut doesn't do a complete evaluation. It answers a simpler, earlier question:

> "Should we continue this migration, or is it already proving to be a bad idea?"

The core of the project is **early-stop decision support for model migration** - not dashboards, experiment tracking, prompt management, or generic evaluation.

## What Driftcut is

- A **pre-evaluation filter**
- A **migration canary**
- A **budget-saving decision layer**
- A tool to decide **whether it's worth continuing**

## What Driftcut is not

- A general eval framework
- An experiment tracking platform
- A prompt optimization system
- A full LLM observability tool
- A replacement for a full evaluation

If your team already uses an eval framework for full evaluations, Driftcut sits _before_ it - the filter that decides whether the full evaluation is worth running.

---

## How it works

Instead of evaluating the entire corpus, Driftcut:

1. **Divides** the corpus into categories. :white_check_mark:
2. **Samples** small, representative batches - prioritizing high-criticality prompts. :white_check_mark:
3. **Compares** baseline and candidate on latency and cost. :white_check_mark:
4. **Runs** deterministic checks and classifies concrete failures such as schema breaks, missing content, and empty outputs. :white_check_mark:
5. **Judges** only ambiguous prompts when semantic comparison is needed. :white_check_mark:
6. **Decides**: stop the test, continue sampling, or declare the candidate ready for full evaluation. :white_check_mark:

The value is **avoiding the discovery - too late - that the test was going badly**.

The same decision pipeline can also be used in replay mode, where historical paired outputs are sampled and evaluated without re-calling the baseline or candidate models.

---

## Three dimensions of comparison

Migration isn't just about output quality. Driftcut compares baseline and candidate across three dimensions:

### Quality :white_check_mark:

Output quality relative to the baseline: format adherence, completeness, correctness, absence of obvious structural breaks.

The current alpha already combines deterministic checks with optional judge-based comparison for ambiguous prompts. The next quality milestone is real light-to-heavy escalation plus richer archetypes beyond the current deterministic set and `judge_worse`.

### Latency :white_check_mark:

Response time of the candidate relative to the baseline.

For many teams, latency is the primary driver of migration - or the reason it fails. Driftcut measures p50, p95, and variance per category, and flags significant latency regressions even when quality is stable.

### Cost :white_check_mark:

Per-prompt cost and total run cost.

Driftcut tracks progressive spend and the spend avoided by stopping an unpromising test early.

---

## Decision engine :white_check_mark:

The decision engine is heuristic-based and explicitly designed as **decision support**, not an infallible oracle.

### Possible outcomes

After each batch, Driftcut produces one of three decisions:

| Decision | Meaning |
|---|---|
| **Stop now** | The candidate is failing critical categories. Abort. |
| **Continue sampling** | Signals are mixed. More data needed. |
| **Proceed to full evaluation** | The candidate looks promising across the board. |

### Stopping logic

**Stop now** if:

- A high-criticality category exceeds the failure threshold (default: 20%)
- Schema breaks are repeated (default: 25% of batch)
- Divergence stays high across consecutive batches

**Continue** if:

- Signals are mixed or unstable
- No severe failures but high variance

**Proceed** if:

- Critical categories remain stable for at least `min_batches`
- Divergence stays below the risk threshold (default: 8%)
- No structural breaks
- Latency shows no significant regressions

### Calibration

Default thresholds are conservative - they favor false negatives (stopping a test that might have been fine) over false positives (approving a candidate that fails in production).

You can and should calibrate them via config. The report shows how close results are to each threshold boundary.

---

## Failure archetypes :white_check_mark:

The report won't just say "quality drop." It classifies concrete failure modes that are already useful in migration triage:

| Archetype | Description |
|---|---|
| **api_error** | Model call still failed after Driftcut retried transient transport/provider errors |
| **empty_output** | Response is empty |
| **json_invalid** | Output is not valid JSON |
| **missing_json_keys** | Required keys are missing from parsed JSON |
| **invalid_labels** | Label output could not be parsed |
| **missing_required_content** | Required substring was not found |
| **forbidden_content** | Forbidden substring was found |
| **overlong_output** | Output exceeded `max_output_chars` |
| **judge_worse** | Judge found the candidate materially worse than baseline |

This turns an abstract score into actionable information. Broader qualitative archetypes such as tone or reasoning degradation are still future work.

---

## The judge cost paradox

Driftcut promises to save budget. But if every comparison requires a judge model call, the judge cost can become significant.

### Tiered strategy

Driftcut addresses this with progressive judge levels:

1. **Deterministic checks (zero cost)** - Is the output valid JSON? Does it match the schema? Is it a refusal? These catch the most obvious failures without spending anything.

2. **Light judge** - For prompts that pass deterministic checks, a small, cheap model (e.g. GPT-4.1-mini) handles general quality comparison.

3. **Heavy judge** - Today you can choose the heavy judge directly. Real automatic escalation from light to heavy is still the next milestone.

A typical canary run (120 prompts, 20% tested, 24 prompts) costs roughly $0.50-$2.00 in judge calls - a fraction of a full evaluation.

---

## Statistical confidence

### Current approach (v0.5.1)

Driftcut uses a pragmatic approach:

- **Stratified sampling** by category and criticality ensures batches are representative
- **Conservative thresholds** minimize the risk of false positives
- **Transparent reporting** shows sample size and corpus coverage so you can judge signal robustness yourself

### Future

Sequential hypothesis testing (SPRT or variants) will provide formal confidence estimates: "with this much data, the probability that the candidate is adequate is above/below threshold X."
