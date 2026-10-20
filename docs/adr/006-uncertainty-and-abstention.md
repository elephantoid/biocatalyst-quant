# ADR-006 — Uncertainty and abstention

**Status:** Accepted

## Decision / agreed direction
S5 hierarchical eligibility/data-quality gates; no forced purchase; maximum 10 stocks and 10% portfolio value target per new slot; unused capital in cash; buy abstention and holding risk/exit rules distinct.

## Initial implementation
Eligibility rules, cash ledger, reason codes

## Open questions and upgrade candidates
Conformal intervals, calibration, dynamic exposure; compare S1/S2/S3.

## Acceptance / checks
- Document exact source and time semantics; do not silently assume missing history.
- Add tests for negative and boundary cases, including missing or delayed data.
- Compare choices on held-out data before promoting a candidate.

## Related decisions
See `../ARCHITECTURE_MASTERPLAN.md` and `../RESEARCH_BACKLOG.md`.
