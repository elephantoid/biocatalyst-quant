# BioCatalyst Quant — Architecture & Engineering Masterplan v1.0

**Research only; no profitability claims.** This document records the outcomes of the architecture discussions. Decisions are not evidence that predictive edge exists.

## Purpose and operating policy
Research US-listed biotech and pharmaceutical clinical/FDA event opportunities using historically accessible public information. Models select entry and exit times. Portfolio is **at most ten stocks**; newly filled positions target **10% of total portfolio value** and unused slots remain cash. S5 hierarchical abstention applies. The research corpus includes eligible firms across many periods, not merely ten tickers or only successful/delisted firms.

## Engineering philosophy
Problem first; benchmark simple deterministic implementations before introducing LLM/RAG/agents/decision models. Use measurable acceptance criteria, evidence-based ADR promotion, provenance, immutable raw data, typed boundaries, local-only quality gates and reproducible experiments. Claude Code is a development assistant, not a runtime dependency or trading agent. No live broker orders without separately approved controls.

## Decisions
- [ADR-001 Temporal data and information availability](adr/001-temporal-data-and-information-availability.md) — Accepted
- [ADR-002 Historical security universe](adr/002-historical-security-universe.md) — Accepted
- [ADR-003 Event identity and market impact](adr/003-event-identity-and-market-impact.md) — Accepted
- [ADR-004 Trade execution realism](adr/004-trade-execution-realism.md) — Accepted
- [ADR-005 Statistical validity](adr/005-statistical-validity.md) — Accepted
- [ADR-006 Uncertainty and abstention](adr/006-uncertainty-and-abstention.md) — Accepted
- [ADR-007 Lineage and indexing](adr/007-lineage-and-indexing.md) — Direction agreed
- [ADR-008 Reproducible research pipeline](adr/008-reproducible-research-pipeline.md) — Accepted v1.1

## End-to-end research DAG
1. **Collect** — source adapters save raw immutable payloads, publish/poll metadata, permissions and hashes.
2. **Normalize & resolve** — company/security/trial/drug/event identifiers; historical ticker histories; disclosure vs update vs cluster.
3. **Validate & snapshot** — temporal constraints, source corroboration, schema and numerical checks, versioned immutable output.
4. **Featurize** — point-in-time only; event type, clinical, financing, market and semantic features; post-event impact is label, not pre-event feature.
5. **Train & validate** — baselines, rolling/expanding purged walk-forward, labels only after available, blocked dependency uncertainty.
6. **Backtest** — 5-min extended-hours bars, 1/5/15/30 latency sensitivity, limit orders, spread/slippage, halt/partial fills, max 10 × 10% and cash.
7. **Evaluate & register** — realistic net performance, event/regime breakdown, baselines, confidence bounds; immutable artifacts and decision lineage.

## Cross-cutting contracts
- **Temporal:** `event_at`, `published_at`, `observed_at`, `historical_eligible_at` (simulated), `live_available_at` (measured), `decision_at`, `order_accepted_at`, `executed_at` with UTC storage and NY market calendar; do not conflate dates with timestamps.
- **Identity:** stable security ID, issuer/CIK, ticker history, NCT ID, intervention/drug, event, disclosure, update and cluster identifiers.
- **Execution:** target portfolio versus realized fills/cash; next **fully eligible** bar; VWAP is a benchmark, not a certain limit-order fill; low/zero-volume bars and halts do not create certain fills.
- **Experiment:** snapshot ID, code and environment versions, stage inputs/hashes, seed, extraction model/prompt/schema, fold IDs, configured latencies, costs, fills and performance.

## Decisions pending data qualification
Intraday/delisted historical provider coverage and license; historical timestamp precision and realistic collection delay; exact order fills and broker permissions; study history API/bulk access; calendar/event source archive completeness. Do not silently mark these as completed.

## Documents
- [Technology decisions](TECHNOLOGY_DECISIONS.md)
- [Data sources](data-sources/DATA_SOURCE_REGISTRY.md)
- [News intelligence](data-sources/NEWS_INTELLIGENCE.md)
- [Qualification protocol](data-sources/QUALIFICATION_PROTOCOL.md)
- [Research backlog](RESEARCH_BACKLOG.md)
- [Local quality gates](LOCAL_QUALITY_GATES.md)
- [Claude Code setup](CLAUDE_CODE_SETUP.md)

## Experiment review / Notion publication
After Stage 07 validates and atomically registers an experiment, an optional outbound Notion sync publishes a whitelisted, immutable experiment summary. It is a non-blocking projection of the local artifact registry; lack of Notion connectivity cannot alter research results. See `docs/NOTION_RESEARCH_LOG.md`.
