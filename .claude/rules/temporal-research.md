# Point-in-time research rules
- Separate event_at, published_at, observed_at, ingested_at, historical_eligible_at, live_available_at, decision_at and execution_time (vocabulary: `docs/DATA_CONTRACTS.md`). Availability is mode-dependent (replay vs live); never default it to published_at. Explicitly document timezones (prefer UTC internally).
- Later revisions to trial data must not overwrite what was knowable in the historical simulation.
- Distinguish company/security/ticker histories and event-document relationships; dedupe repeated press releases.
- Use purged chronological validation, untouched holdout, baseline comparisons and realistic execution constraints.
- Every numeric feature must have a source and transformation provenance. Mark missing as unknown; never impute success outcomes from unavailable future news.
