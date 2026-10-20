# Research Backlog — not committed features

| Origin | Candidate | Why it might matter | Gate to promotion |
|---|---|---|---|
| ADR-001 | Measured publish-to-detect latency, historical timestamp uncertainty | Backtest realism | Prospective timestamp measurements and stress-test sensitivity |
| ADR-002 | Paid delisted/history master, alternate price providers | Survivorship bias | Coverage/license/corporate-action benchmark |
| ADR-003 | 1m/tick bars; overlapping news attribution; discovery-speed modeling | Better timing | Sample of separable updates and available market liquidity |
| ADR-004 | Bid/ask and queue-aware limit fills, broker fill calibration | Executability | Recorded paper fills and replay error benchmarking |
| ADR-005 | CPCV, SPA, PBO; regime-dependent models; time-to-exit models | Overfit resilience | Sufficient effective sample size and preregistered hypotheses |
| ADR-006 | Conformal, ensemble uncertainty, OOD/risk-coverage curves | Abstention quality | OOS improvement in cost-aware risk/coverage vs rule baseline |
| ADR-007 | PostgreSQL, vector DB, OpenLineage and knowledge graph | Indexing/lineage scale | Measured query or trace failures that current tools cannot resolve |
| ADR-008 | MLflow, DVC, Prefect, lakeFS, containers | Reproducibility at scale | Measured manual orchestration/versioning burden |
| Cross-cutting | Feature surprise vs market expectations; specialty news novelty | Potential signal | Publication timestamp proof and independent OOS net trading gain |

Every proposal should track status, hypothesis, owner, dataset, benchmark, acceptance threshold, related ADR and experiment refs before implementation.
