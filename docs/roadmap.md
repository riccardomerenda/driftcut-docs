# Roadmap

## Current status

!!! warning "Pre-release"
    Driftcut is in active development. Phases 1-10 are now materially in place in the alpha: validation, execution, deterministic checks, decision output, HTML reporting, tiered judging for ambiguous cases, historical replay, optional Redis-backed memory with local Docker setup, richer quality scoring with category scorecards, project scaffolding, and corpus bootstrap.

---

## What's built

### Phase 1 - Config, Corpus & Sampling :white_check_mark:

- YAML config loading and validation (Pydantic models)
- Corpus loading from CSV and JSON with full validation
- Stratified batch sampler (high-criticality prioritized in early batches)
- `driftcut validate` CLI command
- CI pipeline (ruff + mypy + pytest on Python 3.12 & 3.13)

### Phase 2 - Migration Runner :white_check_mark:

- Async model execution via LiteLLM (OpenAI, Anthropic, and any LiteLLM-compatible provider)
- Concurrent execution: baseline and candidate run in parallel per prompt
- Latency tracker (p50, p95 per category and overall)
- Cost tracker (per-prompt and cumulative spend)
- `driftcut run` command fully wired end-to-end with Rich progress bars
- JSON results export

### Phase 3 - Deterministic Checks :white_check_mark:

- Format-aware deterministic checks
- JSON validity and required-key checks
- Required / forbidden content checks
- Output length guardrails
- Failure archetype summaries

### Phase 4 - Decision Engine & Reports :white_check_mark:

- Threshold-based `STOP` / `CONTINUE` / `PROCEED` decisions
- `min_batches` as a real proceed guardrail
- High-criticality weighting in overall risk
- Latency thresholds as decision inputs
- HTML report generation
- Richer JSON export with decision history

### Phase 5 - Judge Layer :white_check_mark:

- Semantic comparison for ambiguous cases
- Judge-aware confidence and cost tracking
- Judge details in JSON and HTML output
- `judge_worse` and `judge_unavailable` archetype surfacing

### Phase 6 - Replay Mode :white_check_mark:

- `driftcut replay` for historical paired-output backtesting
- Canonical replay JSON contract with prompt metadata
- Shared deterministic checks, judge flow, and decision engine between live and replay
- Replay-aware JSON and HTML report labeling

### Phase 7 - Memory Layer & Local Dev :white_check_mark:

- Optional Redis-backed baseline response caching for repeated live runs
- Searchable run-history persistence with the same canonical payload used for JSON exports
- Cache-hit, miss, and saved-cost reporting in JSON and HTML outputs
- Docker and Compose assets for reproducible local Redis-backed testing

---

### Phase 8 - Quality Scoring, Polish & Launch :white_check_mark:

- Better per-category quality scoring
- Richer failure archetypes beyond deterministic checks and `judge_worse`
- Category-aware decision reasoning in console, JSON, and HTML output
- HTML reports now show category scorecards and richer semantic failure buckets
- PyPI package publish

---

### Phase 9 - Project Scaffolding :white_check_mark:

- `driftcut init` command to generate a working `migration.yaml` and `prompts.csv`
- `--baseline` and `--candidate` flags for custom model pre-fill
- `--dir` flag for target directory and `--force` flag for overwrite
- Generated files pass `driftcut validate` out of the box

### Phase 10 - Corpus Bootstrap :white_check_mark:

- `driftcut bootstrap --input raw-prompts.txt` command to classify raw prompts via LLM
- Accepts plain text, CSV, and JSON input formats
- Auto-generates IDs, categories, criticality, and expected output types
- Normalizes invalid LLM responses to safe defaults

---

## What's next

### Phase 11 - Launch Polish

- Public demo benchmark

These are not committed. They will only be built if real demand emerges.

- **Sequential hypothesis testing** (SPRT) for more formal confidence estimates
- **Corpus bootstrap helper** to suggest categories and criticality from unstructured prompts
- **CI/CD integration** to run Driftcut as a migration gate in pipelines
- **Web dashboard** for history, cross-run comparison, and collaboration
- **Scheduled checks** for periodic canary runs against production models
