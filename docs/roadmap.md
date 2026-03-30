# Roadmap

## Current status

!!! warning "Pre-release"
    Driftcut is in active development. Phases 1-6 are now materially in place in the alpha: validation, execution, deterministic checks, decision output, HTML reporting, a light judge for ambiguous cases, and historical replay. The next milestone is real light-to-heavy escalation.

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

---

## What's next

### Phase 7 - Escalation, Polish & Launch

- Real tiered light-to-heavy escalation
- Better per-category quality scoring
- Richer failure archetypes beyond deterministic checks and `judge_worse`
- Public demo benchmark
- PyPI package publish

---

## Future ideas (post-MVP)

These are not committed. They will only be built if real demand emerges.

- **Sequential hypothesis testing** (SPRT) for more formal confidence estimates
- **Corpus bootstrap helper** to suggest categories and criticality from unstructured prompts
- **CI/CD integration** to run Driftcut as a migration gate in pipelines
- **Web dashboard** for history, cross-run comparison, and collaboration
- **Scheduled checks** for periodic canary runs against production models
