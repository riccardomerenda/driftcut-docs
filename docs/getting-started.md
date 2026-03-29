# Getting Started

## Installation

Driftcut requires Python 3.12 or later.

```bash
# Clone and install from source (PyPI package coming soon)
git clone https://github.com/riccardomerenda/driftcut.git
cd driftcut
pip install -e .
```

## Prepare your corpus

Driftcut needs a structured prompt corpus — the real prompts your system uses in production. Each prompt must have a category and criticality level.

=== "CSV"

    ```csv
    id,category,prompt,criticality,expected_output_type,notes
    cx-001,customer_support,"Draft a response to: 'I want a refund'",high,free_text,
    ex-001,extraction,"Extract entities from: 'Alice at Acme Corp'",high,json,Must return valid JSON
    cl-001,classification,"Classify this review as positive/negative",medium,labels,
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

## Create a config file

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
```

API keys are loaded from environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).

## Validate your setup

Before spending any money on API calls, validate that your config and corpus are correct:

```bash
driftcut validate --config migration.yaml
```

This prints a summary of your config, corpus stats, and sampling plan — without making any API calls.

## Run a migration test

```bash
driftcut run --config migration.yaml
```

Driftcut will:

1. Sample representative batches from your corpus
2. Run both models on each batch concurrently
3. Track latency (p50, p95) and cost per category
4. Export results to `driftcut-results/results.json`

!!! note "Decision engine coming soon"
    The `run` command executes the migration and collects results. The automatic stop/continue/proceed decision engine is under development.
