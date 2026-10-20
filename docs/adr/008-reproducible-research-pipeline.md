# ADR-008 — Reproducible research pipeline

**Status:** Accepted v1.1

## Decision / agreed direction
Seven stages with contracts: collect -> normalize -> validate/snapshot -> features -> train/validate -> backtest -> evaluate/register. Stage fingerprints, immutable artifacts, atomic publish, single-writer metadata, restart/retry, frozen LLM extraction, independent final-test policy.

## Initial implementation
Git, uv.lock, YAML/Pydantic, DuckDB/Parquet, Python CLI, pytest

## Open questions and upgrade candidates
DVC, MLflow, Prefect/Dagster, lakeFS, containers or distributed jobs conditionally.

## Acceptance / checks
- Document exact source and time semantics; do not silently assume missing history.
- Add tests for negative and boundary cases, including missing or delayed data.
- Compare choices on held-out data before promoting a candidate.

## Related decisions
See `../ARCHITECTURE_MASTERPLAN.md` and `../RESEARCH_BACKLOG.md`.

### Amendment — external research notebook
Completed, locally immutable experiments are mirrored into Notion via official API. This export is asynchronous/outbound, does not participate in the deterministic compute DAG, and does not change local results. Retry and reconcile by experiment ID + summary hash. Treat Notion as a human-review index, not a data/version store.
