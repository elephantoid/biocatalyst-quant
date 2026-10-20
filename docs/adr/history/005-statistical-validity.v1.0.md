# ADR-005 — Statistical validity

**Status:** Accepted

## Decision / agreed direction
Rolling versus expanding purged walk-forward; respect label availability, company/date dependence, multiple comparisons and regime robustness; final untouched/prospective evaluation. Train on historically eligible securities and events, not ex-post winners.

## Initial implementation
Fold manifest, experiment registry, benchmark strategies

## Open questions and upgrade candidates
CPCV/SPA/PBO, regime inference, optimal hold research once evidence supports it.

## Acceptance / checks
- Document exact source and time semantics; do not silently assume missing history.
- Add tests for negative and boundary cases, including missing or delayed data.
- Compare choices on held-out data before promoting a candidate.

## Related decisions
See `../ARCHITECTURE_MASTERPLAN.md` and `../RESEARCH_BACKLOG.md`.
