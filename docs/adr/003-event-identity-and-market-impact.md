# ADR-003 — Event identity and market impact

**Status:** Accepted

## Decision / agreed direction
Separate Event, Disclosure, Information Update, Information Cluster. Before-decision predicted impact and after-event CAR/RVOL/persistence are distinct. Observe extended-hours response; overlapping announcements may only have cluster attribution.

## Initial implementation
Evidence graph, timestamps, event study, 5m bars

## Open questions and upgrade candidates
1-minute/tick resolution; incremental news attribution and confounded events.

## Acceptance / checks
- Document exact source and time semantics; do not silently assume missing history.
- Add tests for negative and boundary cases, including missing or delayed data.
- Compare choices on held-out data before promoting a candidate.

## Related decisions
See `../ARCHITECTURE_MASTERPLAN.md` and `../RESEARCH_BACKLOG.md`.
