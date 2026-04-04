# CLI Reference

Driftcut currently exposes five main commands plus a global version flag.

## Global options

```text
driftcut --version
driftcut -v
```

Print the installed Driftcut version and exit.

## `driftcut init`

Scaffold a new migration config and sample corpus.

```bash
driftcut init
driftcut init --baseline azure/gpt-4-turbo --candidate openrouter/mistral-large
driftcut init --dir ./my-migration
driftcut init --force
```

### Options

| Flag | Required | Default | Description |
|---|---|---|---|
| `--dir`, `-d` | no | `.` | Directory to create files in |
| `--baseline`, `-b` | no | `openai/gpt-4o` | Baseline model in `provider/model` format |
| `--candidate`, `-c` | no | `anthropic/claude-haiku` | Candidate model in `provider/model` format |
| `--force`, `-f` | no | `false` | Overwrite existing files |

### What it does

- Creates a `migration.yaml` with sensible defaults and the specified models
- Creates a `prompts.csv` with 6 sample prompts across 3 categories
- Refuses to overwrite existing files unless `--force` is passed
- The generated files pass `driftcut validate` immediately

## `driftcut bootstrap`

Classify raw prompts into a structured Driftcut corpus using an LLM.

```bash
driftcut bootstrap --input raw-prompts.txt
driftcut bootstrap --input prompts.json --model openai/gpt-4.1-mini --output corpus.csv
driftcut bootstrap --input raw.csv --output prompts.csv --force
```

### Options

| Flag | Required | Default | Description |
|---|---|---|---|
| `--input`, `-i` | yes | none | Path to raw prompts file (`.txt`, `.csv`, or `.json`) |
| `--output`, `-o` | no | `prompts.csv` | Path to write the structured corpus CSV |
| `--model`, `-m` | no | `openai/gpt-4.1-mini` | Model to use for classification |
| `--force`, `-f` | no | `false` | Overwrite existing output file |

### What it does

- Loads prompts from text (one per line or paragraph), CSV (needs a `prompt` column), or JSON (array of strings or objects)
- Sends batches of 20 prompts to the classification model
- Assigns category, criticality, and expected output type to each prompt
- Auto-generates IDs from inferred categories when none are provided
- Writes a standard Driftcut corpus CSV that passes `driftcut validate`

### Input formats

**Text** — one prompt per line, or paragraphs separated by blank lines:

```text
Summarize this article about climate change.
Extract all person names and organizations from the following paragraph.
Classify this customer review as positive, negative, or neutral.
```

**CSV** — must have a `prompt` column, optionally `id`:

```csv
id,prompt
p1,Summarize this article about climate change.
p2,Extract all person names and organizations.
```

**JSON** — array of strings or objects with a `prompt` key:

```json
[
  "Summarize this article about climate change.",
  {"id": "p2", "prompt": "Extract all person names and organizations."}
]
```

## `driftcut validate`

Validate a live-run config and corpus without calling any model APIs.

```bash
driftcut validate --config migration.yaml
driftcut validate -c examples/migration.yaml
```

### Options

| Flag | Required | Description |
|---|---|---|
| `--config`, `-c` | yes | Path to the migration config YAML file |

### What it does

- Loads and validates the YAML config
- Loads and validates the referenced corpus
- Builds the sampling plan
- Prints model, corpus, and threshold summaries

## `driftcut run`

Run a live migration canary against the baseline and candidate models.

```bash
driftcut run --config migration.yaml
driftcut run --config migration.yaml --seed 7
```

### Options

| Flag | Required | Default | Description |
|---|---|---|---|
| `--config`, `-c` | yes | none | Path to the migration config YAML file |
| `--seed` | no | `42` | Random seed for reproducible sampling |

### What it does

- Samples representative prompt batches
- Executes baseline and candidate concurrently
- Retries transient rate limits, timeouts, connection failures, and 5xx responses
- Runs deterministic checks
- Judges ambiguous prompts when enabled
- Updates the `STOP` / `CONTINUE` / `PROCEED` decision after each batch
- Writes `driftcut-results/results.json`
- Writes `driftcut-results/report.html`

## `driftcut replay`

Replay historical paired outputs through the same decision engine without re-calling the baseline or candidate models.

```bash
driftcut replay --config replay.yaml --input replay.json
driftcut replay --config examples/replay.yaml --input examples/replay.json --seed 7
```

### Options

| Flag | Required | Default | Description |
|---|---|---|---|
| `--config`, `-c` | yes | none | Path to the replay config YAML file |
| `--input`, `-i` | yes | none | Path to the canonical replay JSON file |
| `--seed` | no | `42` | Random seed for reproducible replay sampling |

### What it does

- Loads the replay config
- Loads the canonical replay JSON payload
- Reuses the same sampler, deterministic checks, judge flow, and decision engine as live mode
- Writes replay-labeled JSON and HTML outputs

## Output paths

Both `run` and `replay` write outputs under the directory that contains the config file:

```text
driftcut-results/results.json
driftcut-results/report.html
```

`results.json` includes the run mode, decision history, cost summary, per-prompt evaluations, and retry counts for live baseline/candidate responses.
