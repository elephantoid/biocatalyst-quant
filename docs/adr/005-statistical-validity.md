# ADR-005 — Statistical validity

**Status:** Accepted v1.1

## Decision / agreed direction
Support both rolling and expanding purged walk-forward, and compare them; purge training samples by **label availability time**; evaluate on stitched out-of-sample (OOS) predictions; keep an independent final-evaluation dataset that is never used for tuning. Also respect company/date dependence, multiple comparisons and regime robustness. Train on historically eligible securities and events, not ex-post winners.

## Initial implementation
Fold manifest, experiment registry, benchmark strategies

## Open questions and upgrade candidates
CPCV/SPA/PBO, regime inference, optimal hold research once evidence supports it.

**OPEN (not decided in v1.1):** window length, step size and embargo width. They must be fixed in `docs/DESIGN_DECISIONS.md` with evidence before B4 implementation; do not assume defaults.

## Acceptance / checks
- Document exact source and time semantics; do not silently assume missing history.
- Add tests for negative and boundary cases, including missing or delayed data.
- Compare choices on held-out data before promoting a candidate.

## Related decisions
See `../ARCHITECTURE_MASTERPLAN.md` and `../RESEARCH_BACKLOG.md`.

## Revision history
| Version | Change | Original / prior file |
|---|---|---|
| v1.0 | "Rolling versus expanding purged walk-forward; respect label availability ...; final untouched/prospective evaluation." Header carried no version tag. | Preserved verbatim at `history/005-statistical-validity.v1.0.md`, SHA-256 `81d8efbd1f629ed390a473793ba1e3b3497f78a631acf3de182097c86428b8a8` |
| v1.1 | Both rolling and expanding supported; purge keyed to label availability time; stitched OOS predictions; independent final-evaluation data; window/step/embargo kept OPEN. Approved by the user 2026-10-20 (`DD-005`). | v1.1 hash is registered in `../ADR-INTEGRATION.md` (a file cannot contain its own hash). |
