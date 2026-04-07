# Getting Started

!!! tip "Want to see it on a real migration first?"
    The app repo ships an end-to-end demo at [`examples/demo/`](https://github.com/riccardomerenda/driftcut/tree/main/examples/demo) that reproduces a real `gpt-4o` cost-cut decision against `gpt-4o-mini` and `claude-3.5-haiku`. The replay configs run fully offline without an API key, so you can see what Driftcut tells you in about a minute.

## Installation

Driftcut requires Python 3.12 or later.

```bash
# Install from PyPI
pip install driftcut
```

For Redis-backed memory support:

```bash
pip install "driftcut[redis]"
```

If you want the editable developer workflow instead:

```bash
# Clone and install from source
git clone https://github.com/riccardomerenda/driftcut.git
cd driftcut
pip install -e .
```

For local Redis-memory testing without Docker, install the optional extra too:

```bash
pip install -e ".[dev,redis]"
```

### Docker + Redis

For a reproducible local stack, the app repo also ships a `Dockerfile` and `docker-compose.yml`:

```bash
docker compose up -d redis
docker compose run --rm driftcut driftcut validate --config examples/migration.yaml
```

To test the optional Redis-backed memory layer, run the Redis-enabled sample twice:

```bash
docker compose run --rm driftcut driftcut run --config examples/migration.redis.yaml
docker compose run --rm driftcut driftcut run --config examples/migration.redis.yaml
```

The second run should report baseline cache hits in the terminal summary and `driftcut-results/results.json`.

## Scaffold a new project

The fastest way to get started is `driftcut init`:

```bash
driftcut init
```

This generates a working `migration.yaml` and `prompts.csv` in the current directory. You can customize the models:

```bash
driftcut init --baseline azure/gpt-4-turbo --candidate openrouter/mistral-large
```

Or scaffold into a specific directory:

```bash
driftcut init --dir ./my-migration
```

The generated files pass `driftcut validate` immediately — edit the corpus with your real prompts and you are ready to run.

## Bootstrap a corpus from raw prompts

If you have prompts but they aren't categorized yet, `bootstrap` does it for you using an LLM:

```bash
driftcut bootstrap --input raw-prompts.txt --output prompts.csv
```

Accepts `.txt` (one prompt per line or paragraph-separated), `.csv` (must have a `prompt` column), or `.json` (array of strings or objects with a `prompt` key).

```bash
# Custom model and output path
driftcut bootstrap --input prompts.json --model openai/gpt-4.1-mini --output corpus.csv
```

The LLM assigns a category, criticality, and expected output type to each prompt. IDs are auto-generated from the inferred categories. Review and edit the output before running — the LLM suggestions are a starting point, not final.

!!! tip "Bootstrap cost"
    Bootstrap uses a single cheap LLM call per batch of 20 prompts. Classifying 100 prompts typically costs under $0.05 with `gpt-4.1-mini`.

## Prepare your corpus

Driftcut needs a structured prompt corpus: the real prompts your system uses in production. Each prompt must have a category and criticality level, and can optionally include deterministic expectations.

=== "CSV"

    ```csv
    id,category,prompt,criticality,expected_output_type,notes,required_substrings,forbidden_substrings,json_required_keys,max_output_chars
    cx-001,customer_support,"Draft a response to: 'I want a refund'",high,free_text,,refund|replacement,,,
    ex-001,extraction,"Extract entities from: 'Alice at Acme Corp'",high,json,,,,persons|organizations,
    cl-001,classification,"Classify this review as positive/negative",medium,labels,,,,,
    ```

=== "JSON"

    ```json
    [
      {
        "id": "cx-001",
        "category": "customer_support",
        "prompt": "Draft a response to: 'I want a refund'",
        "criticality": "high",
        "expected_output_type": "free_text"
      }
    ]
    ```

### Required fields

| Field | Type | Values |
|---|---|---|
| `id` | string | Unique identifier |
| `category` | string | e.g. `customer_support`, `extraction` |
| `prompt` | string | The prompt to execute |
| `criticality` | enum | `low`, `medium`, `high` |
| `expected_output_type` | enum | `free_text`, `json`, `labels`, `markdown` |
| `notes` | string | Optional context |
| `required_substrings` | list-like string | Optional `|` or `;` separated phrases that must appear |
| `forbidden_substrings` | list-like string | Optional phrases that must not appear |
| `json_required_keys` | list-like string | Optional keys that must exist in parsed JSON |
| `max_output_chars` | integer | Optional hard length cap for deterministic checks |

## Create a config file

=== "Cross-provider"

    Compare models from different providers (requires both API keys):

    ```yaml
    # migration.yaml
    name: "GPT-4o to Claude Haiku migration gate"

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

    evaluation:
      judge_strategy: tiered
      judge_model_light: openai/gpt-4.1-mini
      judge_model_heavy: openai/gpt-4.1
      tiered_escalation_threshold: 0.6
    ```

=== "Same provider"

    Compare models from the same provider (one API key):

    ```yaml
    name: "GPT-4o to GPT-4o-mini cost reduction"

    models:
      baseline:
        provider: openai
        model: gpt-4o
      candidate:
        provider: openai
        model: gpt-4o-mini

    corpus:
      file: prompts.csv
    ```

=== "OpenRouter"

    Use OpenRouter to access any model with a single API key:

    ```yaml
    name: "GPT-4o to Claude Haiku via OpenRouter"

    models:
      baseline:
        provider: openrouter
        model: openai/gpt-4o
      candidate:
        provider: openrouter
        model: anthropic/claude-3.5-haiku

    corpus:
      file: prompts.csv
    ```

=== "Custom endpoint"

    Use `api_base` for Azure, proxies, or self-hosted models:

    ```yaml
    name: "Azure GPT-4o to local Llama"

    models:
      baseline:
        provider: azure
        model: gpt-4o
        api_base: https://my-deployment.openai.azure.com
      candidate:
        provider: openai
        model: meta-llama/llama-3-8b
        api_base: http://localhost:8000/v1

    corpus:
      file: prompts.csv
    ```

Driftcut uses [LiteLLM](https://docs.litellm.ai/) under the hood. Any LiteLLM-supported provider works.

## Set your API keys

The `run` command calls real model APIs. Set the environment variable for your provider(s):

```bash
# Set the key(s) for the providers in your config
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENROUTER_API_KEY="sk-or-..."
```

Only the providers used in your config need keys. The `validate` command does not require API keys.

## Validate your setup

Before spending any money on API calls, validate that your config and corpus are correct:

```bash
driftcut validate --config migration.yaml
```

This prints a summary of your config, corpus stats, and sampling plan without making any API calls.

## Run a migration test

```bash
driftcut run --config migration.yaml
```

Driftcut will:

1. Sample representative batches from your corpus
2. Run both models on each batch concurrently
3. Retry transient provider failures before counting an API error
4. Run deterministic checks on the outputs
5. Judge ambiguous prompts when the strategy is enabled
6. Track latency plus baseline, candidate, and judge cost, plus optional memory stats when enabled
7. Emit a `STOP`, `CONTINUE`, or `PROCEED` decision
8. Export results to `driftcut-results/results.json`
9. Generate `driftcut-results/report.html`

!!! note "Current alpha behavior"
    `judge_strategy: light` compares only ambiguous prompts. `judge_strategy: heavy` uses the heavy judge directly. `judge_strategy: tiered` calls the light judge first and escalates to the heavy judge when confidence is below `tiered_escalation_threshold`.

### What the output looks like

Terminal summary:

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
  Decision:       PROCEED (82% confidence)
```

`driftcut-results/results.json` excerpt:

```json
{
  "mode": "live",
  "decision": {
    "outcome": "PROCEED",
    "confidence": 0.82
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

The HTML report in `driftcut-results/report.html` packages the same run as a shareable summary with threshold context, latency/cost views, failure archetypes, prompt examples, and optional cache visibility.

## Optional Redis memory

If you add a `memory` section to your config, Driftcut can reuse cached baseline responses across repeated live runs and persist full run documents to Redis. Replay mode does not use response caching, but it can still persist run history when memory is enabled.

## Replay a historical comparison

If you already have paired baseline/candidate outputs, you can replay them through the same deterministic checks, judge flow, and decision engine without re-calling the models.

```bash
driftcut replay --config examples/replay.yaml --input examples/replay.json
```

Replay mode expects a canonical JSON payload with prompt metadata plus nested `baseline` and `candidate` outputs. The replay path is intentionally narrow: it is for historical Driftcut backtests, not arbitrary vendor export ingestion.

!!! note "Replay semantics"
    Replay can still incur judge cost if semantic judging is enabled. Historical latency fields are required when `latency.track=true`.

## Compare two runs

After running migration tests with different candidates or configs, compare the results:

```bash
driftcut diff --before driftcut-results/results-v1.json --after driftcut-results/results-v2.json
```

This shows decision changes, metric deltas, per-category risk shifts, cost differences, and which failure archetypes were added or removed. Color-coded output highlights improvements in green and regressions in red.
