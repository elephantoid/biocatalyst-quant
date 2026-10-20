# Technology Decision Matrix

## Core now
- Python 3.12 + uv lock; Git/Claude Code only as development tooling, not research runtime.
- Ruff, strict mypy, pytest, pre-commit/pre-push local gates, Bandit, secret scanning and uv audit (online).
- DuckDB + Parquet; PyArrow, NumPy, pandas, SciPy/statsmodels; Pydantic validation.
- scikit-learn as simple predictive baseline, custom **small** Python CLI DAG/manifest, immutable hashed artifacts and clear tests.
- Simple official-source API adapters; event-study baseline; conservative bar-based execution backtester.

## Conditional after benchmarks
- LightGBM if nonlinear baseline beats simpler models out of sample; Optuna after controlled search design.
- Structured LLM extraction only for fields not safely parsed by deterministic logic; use frozen, evidence-supported output and separate quality metrics.
- Hybrid RAG/BM25/reranking, pgvector only after retrieval recall bottleneck.
- Agent/LangGraph, Jev/Laya or alternative routers only if bench tests beat rules/classifiers and justify costs.
- PostgreSQL if multi-writer bottleneck; MLflow if manual experiment comparisons fail; DVC if caching and dependency tracking become complex; Prefect/Dagster if orchestration complexity demands it; Docker for cross-machine mismatches.

## Research backlog / avoid early adoption
- Graph/GNN, online RL, Bayesian/conformal uncertainty, CPCV/SPA/PBO, regime models, survival/competing risks, order-book/tick execution, lakeFS, distributed experimentation, advanced causality.

## Adoption gate
For every conditional tool record problem, candidate baseline, quality/speed/cost metrics, held-out experiment ID, security/privacy/licensing implications, maintenance cost, rollback and ADR approval. No framework by fashion.

- **Notion official REST API (conditional outbound integration, adopted for experiment journaling):** publish a whitelisted summary from completed local experiments. Store immutable local artifacts as authoritative; add a Notion data source database view only when filtering requirements justify it.
