# ADR-007 — Lineage and indexing

**Status:** Direction agreed

## Decision / agreed direction
Stable document, company, security, drug, trial, event, feature, prediction, decision, order/fill IDs; entity + temporal + lineage lookup, semantic index only when proven necessary; no claim that lineage equals causal attribution.

## Initial implementation
Manifest references, SHA-256, DuckDB/Parquet layout

## Open questions and upgrade candidates
PostgreSQL / pgvector / OpenLineage / graph DB after bottlenecks measured.

## Acceptance / checks
- Document exact source and time semantics; do not silently assume missing history.
- Add tests for negative and boundary cases, including missing or delayed data.
- Compare choices on held-out data before promoting a candidate.

## Related decisions
See `../ARCHITECTURE_MASTERPLAN.md` and `../RESEARCH_BACKLOG.md`.
