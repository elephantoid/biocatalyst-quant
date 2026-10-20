# ADR-002 — Historical security universe

**Status:** Accepted

## Decision / agreed direction
Use security_id distinct from changing ticker and corporate issuer identifier; include delisted issuers and cash/stock corporate-action entitlements; never blanket -100% delistings; compare multiple providers.

## Initial implementation
Security master, ticker history, corporate action log

## Open questions and upgrade candidates
Validate provider delisted coverage, corporate action payout and licensing.

## Acceptance / checks
- Document exact source and time semantics; do not silently assume missing history.
- Add tests for negative and boundary cases, including missing or delayed data.
- Compare choices on held-out data before promoting a candidate.

## Related decisions
See `../ARCHITECTURE_MASTERPLAN.md` and `../RESEARCH_BACKLOG.md`.
