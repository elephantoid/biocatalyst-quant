# ADR-004 — Trade execution realism

**Status:** Accepted

## Decision / agreed direction
5-minute bars including extended hours; baseline 5min post-publication decision latency with 1/5/15/30 sensitivity; separate order transmission; next fully eligible 5min bar; M0 next open, M1 VWAP estimate, M2 conservative limit/volume constraints. Partial and missing fills recorded.

## Initial implementation
Limit order simulator, 1/5/10% volume scenarios, 15min TTL trial

## Open questions and upgrade candidates
Actual bid-ask, queue and broker fill calibration. M1 is not a guaranteed fill.

## Acceptance / checks
- Document exact source and time semantics; do not silently assume missing history.
- Add tests for negative and boundary cases, including missing or delayed data.
- Compare choices on held-out data before promoting a candidate.

## Related decisions
See `../ARCHITECTURE_MASTERPLAN.md` and `../RESEARCH_BACKLOG.md`.
