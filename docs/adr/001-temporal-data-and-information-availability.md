# ADR-001 — Temporal data and information availability

**Status:** Accepted

## Decision / agreed direction
Lightweight bitemporal history; separate actual event, publication, system observation, and hypothetical historical eligible time. Keep live available_at from real measured pipeline logs. Market reaction is a label, not an input.

## Initial implementation
DuckDB + Parquet, immutable source, temporal tests

## Open questions and upgrade candidates
Quantify historical timestamp certainty and measured collection/processing latency.

## Acceptance / checks
- Document exact source and time semantics; do not silently assume missing history.
- Add tests for negative and boundary cases, including missing or delayed data.
- Compare choices on held-out data before promoting a candidate.

## Related decisions
See `../ARCHITECTURE_MASTERPLAN.md` and `../RESEARCH_BACKLOG.md`.
