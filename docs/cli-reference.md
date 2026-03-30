# CLI Reference

Driftcut currently exposes three main commands plus a global version flag.

## Global options

```text
driftcut --version
driftcut -v
```

Print the installed Driftcut version and exit.

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
