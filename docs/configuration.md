# Configuration Reference

Driftcut is configured through a single YAML file. All sections except `name`, `models`, and `corpus` have sensible defaults.

## Full example

```yaml
name: "GPT-4o to Claude Haiku migration gate"
description: "Early-stop migration test for support and extraction workloads"

models:
  baseline:
    provider: openai
    model: gpt-4o
  candidate:
    provider: anthropic
    model: claude-haiku

corpus:
  file: prompts.csv

sampling:
  batch_size_per_category: 3
  max_batches: 5
  min_batches: 2

risk:
  high_criticality_weight: 2.0
  stop_on_schema_break_rate: 0.25
  stop_on_high_criticality_failure_rate: 0.20
  proceed_if_overall_risk_below: 0.08

evaluation:
  judge_strategy: tiered
  judge_model_light: openai/gpt-4.1-mini
  judge_model_heavy: openai/gpt-4.1
  detect_failure_archetypes: true

latency:
  track: true
  regression_threshold_p50: 1.5
  regression_threshold_p95: 2.0

output:
  save_json: true
  save_html: true
  save_examples: true
  show_thresholds: true
  show_confidence: true
```

---

## Section reference

### `models`

**Required.** Defines the two models to compare.

| Field | Type | Description |
|---|---|---|
| `baseline.provider` | string | Provider name (e.g. `openai`, `anthropic`, `openrouter`) |
| `baseline.model` | string | Model identifier |
| `baseline.api_key` | string | Optional. Overrides the environment variable for this model |
| `baseline.api_base` | string | Optional. Custom API endpoint (for proxies, Azure, self-hosted) |
| `candidate.provider` | string | Provider name |
| `candidate.model` | string | Model identifier |
| `candidate.api_key` | string | Optional. Overrides the environment variable for this model |
| `candidate.api_base` | string | Optional. Custom API endpoint |

API keys are loaded from environment variables following each provider's convention (e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`). You can override per-model with the `api_key` field.

Driftcut uses [LiteLLM](https://docs.litellm.ai/) under the hood, so any LiteLLM-supported provider works.

### `corpus`

**Required.** Points to the prompt corpus file.

| Field | Type | Description |
|---|---|---|
| `file` | path | Path to CSV or JSON corpus (relative to config file) |

### `sampling`

Controls how prompts are sampled into batches.

| Field | Default | Description |
|---|---|---|
| `batch_size_per_category` | `3` | Prompts drawn per category per batch |
| `max_batches` | `5` | Hard cap on number of batches |
| `min_batches` | `2` | Planned decision-engine guardrail for minimum evidence before declaring "proceed" |

!!! note "Current alpha behavior"
    The current runner uses `batch_size_per_category` and `max_batches`. `min_batches` is already part of the config schema, but it becomes active when the decision engine lands.

### `risk` *(parsed, not yet active)*

Thresholds that will drive the stop/continue/proceed decision. These values are validated at config load time but have no effect on `run` output until the decision engine is implemented. Defaults are conservative - they favor stopping too early over approving a bad candidate.

| Field | Default | Description |
|---|---|---|
| `high_criticality_weight` | `2.0` | Weight multiplier for high-criticality categories |
| `stop_on_schema_break_rate` | `0.25` | Stop if schema breaks exceed this rate |
| `stop_on_high_criticality_failure_rate` | `0.20` | Stop if high-crit failures exceed this rate |
| `proceed_if_overall_risk_below` | `0.08` | Proceed to full eval if risk stays below this |

!!! tip "Calibrating thresholds"
    Start with defaults. If you find Driftcut stops too aggressively, raise the thresholds. If it lets bad candidates through, lower them. The report will show how close results are to each threshold boundary once the decision layer is implemented.

### `evaluation` *(parsed, not yet active)*

Controls the judge strategy for semantic comparison. These values are validated at config load time but have no effect until the judge adapter is implemented.

| Field | Default | Description |
|---|---|---|
| `judge_strategy` | `tiered` | One of: `none`, `light`, `tiered`, `heavy` |
| `judge_model_light` | `openai/gpt-4.1-mini` | Model for light judging |
| `judge_model_heavy` | `openai/gpt-4.1` | Model for heavy judging (ambiguous cases) |
| `detect_failure_archetypes` | `true` | Classify failures into archetypes |

**Judge strategies:**

- **`none`** - No judge calls. Only deterministic checks (schema, format, refusal). Zero extra cost.
- **`light`** - Use the light model for all semantic comparisons.
- **`tiered`** - Deterministic checks first, light judge for ambiguous cases, heavy judge only when still unclear. Best cost/accuracy balance.
- **`heavy`** - Use the heavy model for all comparisons. Most accurate but most expensive.

### `latency`

Controls latency tracking and regression detection.

| Field | Default | Description |
|---|---|---|
| `track` | `true` | Enable latency measurement |
| `regression_threshold_p50` | `1.5` | Flag if candidate p50 > 1.5x baseline |
| `regression_threshold_p95` | `2.0` | Flag if candidate p95 > 2.0x baseline |

!!! note "Current alpha behavior"
    Latency is measured and reported today. The regression thresholds are validated at config load time and become decision inputs once the quality and decision layers are implemented.

### `output`

Controls what gets saved after a run.

| Field | Default | Status | Description |
|---|---|---|---|
| `save_json` | `true` | :white_check_mark: | Export results as JSON |
| `save_html` | `true` | *coming soon* | Generate HTML report |
| `save_examples` | `true` | *coming soon* | Include failure examples in report |
| `show_thresholds` | `true` | *coming soon* | Show threshold values in report |
| `show_confidence` | `true` | *coming soon* | Show confidence indicator |
