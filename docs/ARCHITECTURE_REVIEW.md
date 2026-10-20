> **SUPERSEDED (2026-10-20) — historical record only. Do not use as a current requirement.**
> Current authoritative sources: [`ADR-INTEGRATION.md`](ADR-INTEGRATION.md) (ADR-001~008 + hashes),
> [`adr/`](adr/) (ADRs), [`PROJECT_SPEC.md`](PROJECT_SPEC.md), [`DESIGN_DECISIONS.md`](DESIGN_DECISIONS.md),
> [`DATA_CONTRACTS.md`](DATA_CONTRACTS.md), [`STATUS.md`](STATUS.md).
> Known divergence: this review's "exactly ten stocks" conflicts with ADR-006 (max 10 slots, 10% per new slot,
> unused slots in cash); ADR-006 governs. Body below is preserved unmodified.

# Architecture Review — 2026-10-16

## Accepted scope

- Train and validate A: pre-catalyst, B: outcome probability, C: post-event response, then D: combined.
- Historical research universe: at least 30 companies; pursue materially more events and companies.
- Live/paper strategy target: **exactly ten stocks, equal initial dollar weights**; model selects entry and exit.
- Historical replay must use ten-stock portfolios too; don't confuse number of research observations and live holdings.
- Define a fallback when fewer than ten eligible stocks exist (cash or no-trade); compare policies, never silently fill slots.

## P0 issues to resolve before a credible backtest

1. **Point-in-time leakage**: maintain event time, first publication, ingestion time, and decision-available time; preserve original snapshots and document hashes. Enforce `available_at <= decision_at`.
2. **Survivorship and corporate actions**: reconstruct historical security identifiers, delistings, mergers, splits, ticker history, and actionable price bars. Define treatment of bankrupt/delisted symbols.
3. **Event ontology / identity**: entity-resolution mapping CIK, NCT ID, drug, indication and event ID. Join repeated press releases into one underlying event while preserving revision sequence.
4. **Execution realism**: model pre-market/post-market event timestamps in America/New_York and DST, next executable bar, spread, slippage, halts, bid/ask, liquidity, dilution, transaction costs and missed fills.
5. **Inference validity**: purge overlapping labeling windows, embargo adjacent splits as needed, cluster by issuer and time, account for multiple comparisons and regime shifts. Never tune on final holdout.

## P1 issues

6. **Uncertainty and abstention**: unknown fields, contradiction queues, failed validation quarantine, no forced hallucinated default; explicit 10-stock shortage policy.
7. **Lineage**: every feature and trade references source/version, extraction prompt/model, validation result, feature code and training artifact.
8. **Reproducibility**: `uv.lock`, schema version, timezone conventions, seeds, data hashes, Git SHA, reproducible environment and experiment manifest.

## Additional acceptance gates

- Dataset licensing and redistribution restrictions; SEC/FDA/API fair-use/rate limits; broker/market-data rights.
- Regulatory and operational risk review before live order connectivity; isolate paper and live credentials.
- Stock selection biased by missing source history must be measured (coverage by year, issuer, event type).
- Compare against XBI/IBB/SPY and simple ten-stock baselines on matched dates/capital, after costs.
- Distinguish model uncertainty, financial loss tail risk and operational outage risk; kill switch for live trading.
- Avoid training LLM extractors on evaluation labels; split gold samples by underlying event, not documents.

## Decision log

Every promoted technique needs a documented task, baseline, test set, metric, cost, tradeoff, failure behavior and ADR. Agent/RAG/LLM are not defaults.
