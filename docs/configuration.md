# Configuration Reference

Driftcut is configured through a single YAML file. All sections except `name` and `models` have sensible defaults. `corpus` is required for live `run`, but replay mode gets prompt metadata from the replay input file instead.

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
  tiered_escalation_threshold: 0.6
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

API keys are loaded from environment variables following each provider's convention such as `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `OPENROUTER_API_KEY`. You can override per-model with the `api_key` field.

Driftcut uses [LiteLLM](https://docs.litellm.ai/) under the hood, so any LiteLLM-supported provider works.

!!! note "Live call reliability"
    In `v0.7.0`, live `run` calls automatically retry transient rate limits, timeouts, connection failures, and 5xx responses before Driftcut records an `api_error`. Saved JSON artifacts include `retry_count` for each baseline/candidate response.

### `corpus`

**Required.** Points to the prompt corpus file.

| Field | Type | Description |
|---|---|---|
| `file` | path | Path to CSV or JSON corpus (relative to config file) |

The current corpus format also supports optional deterministic expectation fields such as `required_substrings`, `forbidden_substrings`, `json_required_keys`, and `max_output_chars`.

### `sampling`

Controls how prompts are sampled into batches.

| Field | Default | Description |
|---|---|---|
| `batch_size_per_category` | `3` | Prompts drawn per category per batch |
| `max_batches` | `5` | Hard cap on number of batches |
| `min_batches` | `2` | Minimum evidence before Driftcut can declare `PROCEED` |

!!! note "Current alpha behavior"
    `min_batches` is active in `v0.7.0`: Driftcut will not declare `PROCEED` until at least this many batches have been evaluated.

### `risk`

Thresholds that drive the stop/continue/proceed decision. Defaults are conservative and favor stopping too early over approving a bad candidate.

| Field | Default | Description |
|---|---|---|
| `high_criticality_weight` | `2.0` | Weight multiplier for high-criticality categories |
| `stop_on_schema_break_rate` | `0.25` | Stop if schema breaks exceed this rate |
| `stop_on_high_criticality_failure_rate` | `0.20` | Stop if high-crit failures exceed this rate |
| `proceed_if_overall_risk_below` | `0.08` | Proceed to full eval if risk stays below this |

!!! tip "Calibrating thresholds"
    Start with defaults. If Driftcut stops too aggressively, raise the thresholds. If it lets bad candidates through, lower them. The report shows how close results are to each threshold boundary.

### `evaluation`

Controls judge behavior for semantic comparison after deterministic checks.

| Field | Default | Description |
|---|---|---|
| `judge_strategy` | `light` | One of: `none`, `light`, `tiered`, `heavy` |
| `judge_model_light` | `openai/gpt-4.1-mini` | Model for light judging |
| `judge_model_heavy` | `openai/gpt-4.1` | Model for heavy judging |
| `tiered_escalation_threshold` | `0.6` | Escalate from light to heavy when confidence falls below this threshold |
| `detect_failure_archetypes` | `true` | Classify failures into archetypes |

**Judge strategies:**

- **`none`** - No judge calls. Only deterministic checks. Zero extra cost.
- **`light`** - Judge only ambiguous prompts with the light model.
- **`tiered`** - Judge ambiguous prompts with the light model first, then escalate to the heavy model when confidence is below `tiered_escalation_threshold`.
- **`heavy`** - Judge ambiguous prompts with the heavy model instead of the light model.

### `latency`

Controls latency tracking and regression detection.

| Field | Default | Description |
|---|---|---|
| `track` | `true` | Enable latency measurement |
| `regression_threshold_p50` | `1.5` | Flag if candidate p50 is greater than 1.5x baseline |
| `regression_threshold_p95` | `2.0` | Flag if candidate p95 is greater than 2.0x baseline |

!!! note "Current alpha behavior"
    Latency is measured and reported today. The thresholds are active decision inputs in `v0.7.0`.

### Replay mode

Replay mode uses the same `sampling`, `risk`, `evaluation`, `latency`, and `output` sections, but it reads prompt metadata plus paired baseline/candidate outputs from a canonical replay JSON file:

```bash
driftcut replay --config replay.yaml --input replay.json
```

The replay input contract is versioned and intentionally narrow. Each record must include:

- prompt metadata such as `id`, `category`, `prompt`, `criticality`, and `expected_output_type`
- nested `baseline` and `candidate` objects
- either `output` or `error` for each side
- `latency_ms` when `latency.track=true`

Historical model cost is optional. Replay-time judge cost is tracked separately in the report when semantic judging is enabled.

### `memory`

Optional. Enables the Redis-backed memory layer for baseline response caching and run-history persistence.

```yaml
memory:
  backend: redis
  redis_url: redis://localhost:6379/0
  namespace: driftcut-dev
  response_cache:
    enabled: true
    ttl_seconds: 604800
  run_history:
    enabled: true
    ttl_seconds: 2592000
```

| Field | Default | Description |
|---|---|---|
| `backend` | `redis` | Current memory backend |
| `redis_url` | none | Redis connection URL |
| `namespace` | `driftcut` | Prefix used for cache and run-history keys |
| `response_cache.enabled` | `true` | Reuse cached baseline responses in live runs |
| `response_cache.ttl_seconds` | `604800` | Cache TTL in seconds (7 days) |
| `run_history.enabled` | `true` | Persist completed run payloads to Redis |
| `run_history.ttl_seconds` | `2592000` | Run-history TTL in seconds (30 days) |

!!! note "Baseline cache semantics"
    Cached baseline responses are intentionally excluded from live latency comparison. Driftcut reuses the output and records cache hits and saved baseline cost, but it does not treat cached latency as fresh live latency evidence.

!!! note "Failure behavior"
    Redis is optional. If the memory layer is disabled, Driftcut behaves exactly as before. If Redis is configured but temporarily unavailable at runtime, Driftcut falls back to the normal live path instead of failing the migration gate.

### `output`

Controls what gets saved after a run.

| Field | Default | Status | Description |
|---|---|---|---|
| `save_json` | `true` | :white_check_mark: | Export results as JSON |
| `save_html` | `true` | :white_check_mark: | Generate HTML report |
| `save_examples` | `true` | :white_check_mark: | Include failure examples in report output |
| `show_thresholds` | `true` | :white_check_mark: | Show threshold values in report output |
| `show_confidence` | `true` | :white_check_mark: | Show confidence indicator |
