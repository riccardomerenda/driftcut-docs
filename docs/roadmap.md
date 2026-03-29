# Roadmap

## Current status

!!! warning "Pre-release"
    Driftcut is in active development. Phase 1 is complete. The `validate` command works today; the `run` command is coming soon.

---

## What's built

### Phase 1 — Config, Corpus & Sampling :white_check_mark:

- YAML config loading and validation (Pydantic models)
- Corpus loading from CSV and JSON with full validation
- Stratified batch sampler (high-criticality prioritized in early batches)
- `driftcut validate` CLI command
- CI pipeline (ruff + pytest on Python 3.12 & 3.13)

---

## What's next

### Phase 2 — Migration Runner

- Async model execution via LiteLLM (OpenAI, Anthropic)
- Latency tracker (p50, p95 per category)
- Cost tracker (per-prompt and cumulative)
- Batch-level result storage

### Phase 3 — Deterministic Checks & Judge

- Schema validation, format checks, refusal detection (zero-cost)
- Tiered judge adapter (light → heavy escalation)
- Failure archetype classifier
- Per-category quality scoring

### Phase 4 — Decision Engine

- Early-stop logic with configurable thresholds
- Category weighting (high-criticality multiplier)
- Batch-over-batch trend detection
- Four-way decision output: stop / continue / proceed / proceed-partial

### Phase 5 — Reports & Export

- Rich terminal report with decision, evidence, and failure breakdown
- JSON export of full results
- HTML report generation
- Confidence indicator
- Threshold proximity display

### Phase 6 — Polish & Launch

- CLI help and error messages
- Sample synthetic dataset
- Public demo benchmark
- PyPI package publish

---

## Future ideas (post-MVP)

These are not committed — they'll be built only if real demand emerges.

- **Sequential hypothesis testing** (SPRT) for formal confidence estimates
- **Corpus bootstrap helper** — suggest categories and criticality from unstructured prompts
- **CI/CD integration** — run Driftcut as a migration gate in pipelines
- **Web dashboard** — history, comparison across runs, team collaboration
- **Scheduled checks** — periodic canary runs against production models
