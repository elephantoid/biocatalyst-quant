# Python Engineering Standards v1.0

## Philosophy

**Problem First, Technology Second.** Choose the simplest verifiable approach; add LLM, agents, RAG, or sophisticated ML only after benchmarking against a simpler baseline. Architecture Decision Records (ADR) are required for meaningful dependencies or abstraction shifts.

## Supported language and dependency policy

- Baseline Python **3.12** (allow 3.13 only after compatibility is verified). `uv` manages packages and lockfiles; commit `uv.lock`. Do not hand-edit it.
- Source layout `src/biocatalyst_quant/`; package installation should not depend on working-directory hacks or `sys.path` manipulation.
- Production and development requirements are separate in `pyproject.toml`; upgrade dependencies in explicit, reviewed PRs.
- Keep research notebooks for exploration, but move reusable logic to typed `src/` modules with tests.
- Never commit credentials, private financial data, paid feeds or unlicensed redistributed articles.

## Style and structure

- Ruff formatter and lint, line length **100**, four-space indentation, double quotes, absolute imports, no wildcard imports.
- Prefer simple composition over inheritance. One unit of domain responsibility per module. Name domain concepts explicitly (`first_public_at`, not `time`).
- Prefer pure functions and immutable dataclasses at the calculation boundary; separate I/O adapters from domain logic.
- Use `pathlib.Path`, timezone-aware UTC datetimes internally and explicit exchange-local timezone conversion at ingestion/execution boundary.
- Avoid `print` in library code; use structured logging with event/source/trace IDs; never log secrets.
- No bare `except`, silent coercion, mutable default arguments, magic numeric constants, or magic test fixtures.
- Handle missing information with explicit `None`/typed result or a domain exception; never manufacture a research label.
- Docstrings for public modules/functions/classes: explain meaning, units, timing assumptions, side effects; do not paraphrase function names.
- Comments explain **why**, not obvious **what**. Cite papers and source URLs/IDs near scientific assumptions.

## Typing

- Every public function argument and return type must be annotated; use `mypy strict` on `src/`.
- Prefer `dataclass(frozen=True, slots=True)` for domain values; use `Protocol` for interchange boundaries.
- Use `Literal`, enums, and tagged results for event outcome states; avoid ambiguous booleans.
- Differentiate monetary units, return fractions (0.05), percentages (5%), price, shares, datetime and trading day in names/types. Consider `NewType` when errors recur.
- Use `Any` only at unavoidable external boundaries, validate and narrow immediately. A passing type checker is not a substitute for runtime schema validation.
- Numerical work: state precision, missing-data strategy, data alignment, rounding policy; no accidental float equality assertions.

## API and data contracts

- Each pipeline transformation documents input schema, output schema, invariants, timezone, nullability, provenance, side effects and failure policy.
- Use stable `security_id`/`event_id`, not mutable ticker symbols, for relational joins.
- Model `event_at`, `published_at`, `observed_at`, `ingested_at`, `historical_eligible_at`, `live_available_at`, `decision_at` separately (vocabulary: `DATA_CONTRACTS.md`).
- Raw data append-only and content-hashed; normalized data versioned; features carry source and extraction versions.
- Data ingestion must be idempotent, retryable with backoff, rate-limited, and checkpointed.

## Required developer loop

```bash
uv sync
uv run ruff format .
uv run ruff check . --fix
uv run mypy src
uv run pytest -m 'not external' --cov=biocatalyst_quant --cov-branch
```

Before pushing, use non-mutating checks:

```bash
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy src
uv run --locked pytest -m 'not external' --cov=biocatalyst_quant --cov-branch
```

## PR review checklist

- [ ] Required behavior and baseline stated; no gratuitous framework.
- [ ] Meaningful types, clear names, boundary validation and failure states.
- [ ] Unit and integration tests cover normal, edge, malformed and timestamp-leakage cases.
- [ ] Provenance and point-in-time semantics preserved.
- [ ] No accidental network calls in unit tests; deterministic fixtures and clock.
- [ ] Dependencies, licenses, secrets and data contracts reviewed.
- [ ] Relevant ADR and experiment manifest updated.
- [ ] Formatter, lint, strict typing, tests, CI pass.
