# DESIGN DECISIONS LOG

> Never silently rewrite accepted ADRs or retrofit a rationale. Log proposed and accepted changes separately.

> Note: entries below cite `diff.md` (a one-off 2026-10-20 cross-version audit). It is no longer tracked (kept locally in git-ignored `local-docs/`); everything it established is carried by these DD entries and `ADR-INTEGRATION.md`.

## TEMPLATE (copy per decision)
- Date / decision ID:
- Problem and source evidence:
- Existing constraint / prior ADR:
- Option A / Option B:
- Expected advantage / cost / failure condition:
- Fastest distinguishing experiment:
- User decision: **PENDING | APPROVED | REJECTED**
- Code/test links:

---

## DD-001 — Cross-Version (`v1.0` / `v1.1` / `v2.0`) Consolidation & Inventory Baseline
- **Date / decision ID**: 2026-10-20 / `DD-001`
- **Problem and source evidence**: Three directory snapshots existed (`biocatalyst-quant _v1.0`, `biocatalyst-quant_v1.1`, and the `v2.0` governance workspace). `v1.1` added the `ADR-008 v1.1` Notion experiment journal amendment and `notion_experiments.py`, while `v2.0` introduced strict single-task build governance (`AGENTS.md`, `CLAUDE.md`, `BUILD_PROMPT.md`, `PROJECT_SPEC.md`, `ACCEPTANCE.md`, `ADR-INTEGRATION.md`, `BACKLOG.md`).
- **Existing constraint / prior ADR**: `PROJECT_SPEC.md` requires preserving `ADR-001`~`008` originals and completing `B0` inventory before resuming implementation.
- **Option 1 / Option 2**:
  - **Option 1**: Sync all `v1.1` files into the workspace while preserving `v2.0` governance files (`AGENTS.md`, `CLAUDE.md`, `BUILD_PROMPT.md`, etc.), and document all 6 cross-version discrepancies in `diff.md`, `docs/ADR-INTEGRATION.md`, and `docs/STATUS.md`.
  - **Option 2**: Keep only `v1.0` files and omit `v1.1` Notion integration files.
- **Expected advantage / cost / failure condition**:
  - Option 1 preserves the true `ADR-008 v1.1` text and code while exposing `notion_experiments.py` quality-gate gaps (`mypy strict`, `ruff`, `bandit`) early as `partial`.
- **Fastest distinguishing experiment**: `shasum -a 256 docs/adr/*.md` and cross-file audit in `diff.md`.
- **User decision**: **APPROVED (Option 1)**
- **Code/test links**: `diff.md` (local-only), [`docs/ADR-INTEGRATION.md`](ADR-INTEGRATION.md), [`docs/STATUS.md`](STATUS.md)

---

## DD-002 — `B1-01` Point-in-Time Timestamp Hierarchy & Historical Universe Fixture Design
- **Date / decision ID**: 2026-10-20 / `DD-002`
- **Problem and source evidence**: Current [`src/biocatalyst_quant/domain.py`](../src/biocatalyst_quant/domain.py) only records a single `available_at` timestamp on `HistoricalFeature` and has zero representation of `event_at`, `published_at`, `observed_at` (`ingested_at`), or `historical_eligible_at` (simulated) vs `live_available_at` (measured), nor any historical security universe (`security_id` vs mutable ticker, delisting settlement, corporate action adjustments).
- **Existing constraint / prior ADR**: [`ADR-001`](adr/001-temporal-data-and-information-availability.md), [`ADR-002`](adr/002-historical-security-universe.md), [`DATA_CONTRACTS.md`](DATA_CONTRACTS.md), [`ACCEPTANCE.md`](ACCEPTANCE.md) (must prove differences among publication/observation/available-at timestamps in tests, and include survivorship, delisting, and corporate action counterexamples).
- **Option A / Option B**:
  - **Option B1-A (Pure Stdlib Frozen Dataclasses + Deterministic In-Memory Fixtures)**:
    - Model `TemporalRecord` (`event_at`, `published_at`, `observed_at`, `available_at`, `availability_mode: Literal["historical_simulated", "live_measured"]`) and `SecurityMasterRecord` / `TickerInterval` / `DelistingEvent` / `CorporateAction` using Python standard library `@dataclass(frozen=True, slots=True)` in `src/biocatalyst_quant/`, keeping `dependencies = []` in `pyproject.toml`.
    - Build unit/integration test fixtures covering: (1) `event_at < decision_at < published_at` rejected, (2) `published_at < decision_at < available_at` (latency window) rejected, (3) naive timestamps rejected, (4) ticker reuse/rename across two different `security_id`s, (5) cash-merger delisting payout (+20% or -40%, not blanket -100%), and (6) reverse split share/price adjustment as of `ex_date`.
  - **Option B1-B (Immediate DuckDB + Pydantic Table Fixtures)**:
    - Add `duckdb`, `pyarrow`, and `pydantic` to `pyproject.toml` runtime dependencies now and implement `B1-01` fixtures as SQL queries over DuckDB tables.
- **Expected advantage / cost / failure condition**:
  - **Option B1-A Advantage**: Zero new dependencies, fast deterministic execution, 100% branch coverage achievable immediately, and cleanly isolates domain invariants from storage adapters.
  - **Option B1-A Failure Condition**: If timezone conversion or interval overlap rules (`[effective_from, effective_to)`) are underspecified at boundaries, point-in-time ticker resolution could return two securities or drop a security on the exact timestamp of a corporate action.
  - **Option B1-B Cost/Failure Condition**: Mutates `pyproject.toml` stack before domain invariants (`B1`–`B5`) are verified and couples unit tests to DuckDB SQL semantics.
- **Fastest distinguishing experiment**: Focused unit test suite in `tests/unit/test_temporal_and_universe.py` testing boundary instants (`decision_at == published_at`, `decision_at == available_at`, and exact delisting/split boundary timestamps).
- **User decision**: **PENDING**
- **Annotation (2026-10-20, added without altering the text above)**: field names in Option B1-A (`available_at`, `availability_mode`) predate `DD-004`. If `B1-01` is approved, the model must use the `DD-004` vocabulary (`observed_at` and `ingested_at` separate; `historical_eligible_at` / `live_available_at` instead of a single `available_at`).
- **Code/test links**: [`src/biocatalyst_quant/domain.py`](../src/biocatalyst_quant/domain.py), [`tests/unit/test_domain.py`](../tests/unit/test_domain.py)

---

## DD-003 — Local environment bootstrap and local-only artifact policy
- **Date / decision ID**: 2026-10-20 / `DD-003` (`.gitignore` already referenced this ID)
- **Problem and source evidence**: `STATUS.md` claimed `.git`, `uv.lock`, `.venv` were missing; inspection found all three present (`.git` with zero commits, no remote, no parent repo; `uv.lock` 37 packages; `.venv` Python 3.12.13). Missing: `.secrets.baseline`, tracked files (so `quality.sh` could not scan).
- **Existing constraint / prior ADR**: ADR-008 (Git, uv.lock); `docs/LOCAL_QUALITY_GATES.md` bootstrap; user conditions Q4 (no re-init over existing history, no secrets/data/large files in Git, Python 3.12, empty scan must fail, never delete local data).
- **Option A / Option B**:
  - **A**: Keep the existing empty repo, stage files (no commit), generate `.secrets.baseline`, install hooks.
  - **B**: `rm -rf .git && git init` or regenerate `uv.lock`/`.venv`.
- **Expected advantage / cost / failure condition**: A is non-destructive and satisfies Q4. B risks destroying unknown state for no gain. A fails if `git add` pulls in sensitive/large files: checked via ignore rules (no `.env`, parquet, duckdb, pkl, `data/`, `experiments/`, `settings.local`) and no tracked file >500 KB (largest: `uv.lock`, 91 KB; the only >500 KB file is the git-ignored `.mypy_cache`).
- **Fastest distinguishing experiment**: `git add -n .` review; `detect-secrets scan` (0 findings); `bash scripts/quality.sh full`.
- **User decision**: **APPROVED (Option A, conditional — Q4)**
- **Code/test links**: [`scripts/quality.sh`](../scripts/quality.sh) (already fails when the scan list is empty — verified in an empty scratch repo; no change needed), [`.secrets.baseline`](../.secrets.baseline), [`.gitignore`](../.gitignore)

---

## DD-004 — Temporal vocabulary (ADR-001 clarification, not an amendment)
- **Date / decision ID**: 2026-10-20 / `DD-004`
- **Problem and source evidence**: `diff.md` #5 — four documents used different field sets (`ingested_at` vs `observed_at`, single `available_at`).
- **Existing constraint / prior ADR**: ADR-001 (event, publication, system observation, hypothetical historical eligible time; live available_at from measured logs). Meaning unchanged.
- **Option A / Option B**:
  - **A**: `observed_at` and `ingested_at` distinct; availability split by mode into `historical_eligible_at` / `live_available_at`.
  - **B**: Treat `observed_at` ≡ `ingested_at` and keep one `available_at`.
- **Expected advantage / cost / failure condition**: A separates discovery latency from storage latency and prevents replay from borrowing live timestamps; cost is more fields. B is simpler but hides a leakage source (discovered ≠ durably stored ≠ usable).
- **Fastest distinguishing experiment**: B1-01 boundary tests (`decision_at` equal to each timestamp).
- **User decision**: **APPROVED (Option A — Q1)**
- **Code/test links**: [`DATA_CONTRACTS.md`](DATA_CONTRACTS.md), [`PYTHON_ENGINEERING_STANDARDS.md`](PYTHON_ENGINEERING_STANDARDS.md), [`TESTING_STRATEGY.md`](TESTING_STRATEGY.md), `.claude/rules/temporal-research.md`. Code (`domain.py` `available_at`) intentionally **not** changed: deferred to `B1-01`.

---

## DD-005 — ADR-005 v1.0 → v1.1
- **Date / decision ID**: 2026-10-20 / `DD-005`
- **Problem and source evidence**: `diff.md` #3 — `ADR-INTEGRATION.md` already described "v1.1" semantics while the ADR file said "Accepted" with "Rolling versus expanding".
- **Existing constraint / prior ADR**: ADR-005 v1.0 (SHA-256 `81d8efbd…8b8a8`); `DESIGN_DECISIONS.md` rule "never silently rewrite accepted ADRs".
- **Option A / Option B**:
  - **A**: Revise in place to v1.1, keep v1.0 verbatim in `docs/adr/history/`, register both hashes and a revision table.
  - **B**: Leave the ADR and only fix `ADR-INTEGRATION.md` wording.
- **Expected advantage / cost / failure condition**: A removes the doc/ADR contradiction with a verifiable audit trail; cost is one extra file. Failure: someone edits `history/` — mitigated by the recorded hash.
- **Fastest distinguishing experiment**: `shasum -a 256 docs/adr/history/005-statistical-validity.v1.0.md` equals the v1.0 hash.
- **User decision**: **APPROVED (Option A — Q2)**; window, step and embargo remain **OPEN**.
- **Code/test links**: [`adr/005-statistical-validity.md`](adr/005-statistical-validity.md), [`adr/history/005-statistical-validity.v1.0.md`](adr/history/005-statistical-validity.v1.0.md), [`ADR-INTEGRATION.md`](ADR-INTEGRATION.md)

---

## DD-006 — Bandit B310/B311 handling
- **Date / decision ID**: 2026-10-20 / `DD-006`
- **Problem and source evidence**: `bandit --ignore-nosec` reports exactly two findings in `notion_experiments.py`: `B311` (jitter) and `B310` (`urlopen`).
- **Existing constraint / prior ADR**: `LOCAL_QUALITY_GATES.md` ("review false positives rather than globally silencing"); user condition Q3.
- **Option A / Option B**:
  - **A**: Line-scoped `# nosec <ID>` with a stated reason (already present).
  - **B**: Replace `random.random()` with `secrets`, and `urlopen` with a hardened opener.
- **Expected advantage / cost / failure condition**: B311 — jitter only, no security property: A is correct, `secrets` adds noise. B310 — URL is `API + endpoint`, rejected unless it starts with `https://api.notion.com/`, so `file:`/custom schemes cannot reach `urlopen`: A is justified. **Residual risk (not fixed)**: `urllib` follows redirects and may forward the `Authorization` header; Notion does not normally redirect, and a no-redirect opener would change the test seam. Also `parent_id` (from env) was interpolated into a URL path without format validation — **resolved 2026-10-20**: `validate_page_id` (32-hex/UUID) in `main()` and `NotionAPI.find_child_page`, plus `quote(safe="")`; tests `test_page_id_*`. The redirect/`Authorization` risk is still open.
- **Fastest distinguishing experiment**: `bandit -r src` (pass) and `bandit -r src --ignore-nosec` (exactly these two lines).
- **User decision**: **APPROVED (Option A, line-scoped only — Q3)**; no global skips exist (`grep` over `pyproject.toml`/source).
- **Code/test links**: [`notion_experiments.py`](../src/biocatalyst_quant/integrations/notion_experiments.py) (`_jitter`, `NotionAPI.call`); `test_call_refuses_non_notion_origin`.

---

## DD-007 — Notion sync stability (`B6-02`, not full `B7`)
- **Date / decision ID**: 2026-10-20 / `DD-007`
- **Problem and source evidence**: `STATUS.md`/`diff.md` #2 listed type, lint, bandit failures. Measured on 2026-10-20: `ruff check` 1 error (PT018, test l.238), `mypy --strict` 1 error (`no-any-return`, l.131). The other listed problems (None-typed `api`, long lines, `nosec`, retry loop, reconcile) were already fixed in the file — not re-fixed.
- **Existing constraint / prior ADR**: ADR-008 v1.1 Amendment (outbound, non-blocking, retry/reconcile by experiment ID + summary hash).
- **Option A / Option B**:
  - **A**: Fix only the two failing checks; record the Q5 coverage matrix.
  - **B**: Add an outbox/state machine now.
- **Expected advantage / cost / failure condition**: A is minimal and meets "quality only". B is `B7` scope (not approved). Failure of A: duplicate window remains between the existence check and `POST` for concurrent writers (documented; single writer required).
- **Fastest distinguishing experiment**: ruff + mypy + the 31 Notion tests.
- **Q5 coverage**: `experiment_id`+hash title dedupe — **done** (`test_remote_idempotency`, `test_deterministic_title_and_revision`). Re-lookup after ambiguous write — **done** (`test_ambiguous_write_reconciles_without_second_create`). Bounded retries, explicit failure — **done** (`MAX_ATTEMPTS`, `RECONCILE_ATTEMPTS`, `test_ambiguous_write_unresolved_fails_with_bounded_lookups`). Completion vs sync status separated — **partial** (module never touches local artifacts and failure JSON carries `sync_status`; success output still uses a bare `status` key; no persisted sync state). Outbox non-blocking publish — **deferred to `B7`**.
- **User decision**: **APPROVED (Option A — Q5)**
- **Follow-up hardening (2026-10-20, from the automated security review; user approved)**:
  - `metrics.json` was mirrored whole, contradicting the documented "whitelisted metrics only". Now `whitelist_metrics`: explicit key allow-list (`ALLOWED_METRIC_KEYS`), finite scalar values only, text ≤200 chars; violations are **rejected, not dropped**, so publication stops. The key list is the author's draft; extend it deliberately. Limitation: an allowed key can still carry a bad string value (length-capped only).
  - `parent_id` validated and percent-encoded (see `DD-006`).
  - `scripts/quality.sh` secret scan is NUL-delimited and fails closed on empty list or a tracked path missing on disk.
  - `.claude/settings.json` allow-list narrowed to fixed-argument commands (the old `git diff *` / `pytest *` could read `.env` via `--no-index` or load plugins via `-p`); Bash-level `.env` denies added as friction only — Read-deny rules never constrained Bash.
  - **Accepted, not fixed (B7)**: an existing page with the same title is trusted as "already published". Only someone with edit access to the parent page can forge that, and that person already controls the journal. A local sync ledger (outbox) and content-hash verification of the found page belong to B7.
- **Code/test links**: [`notion_experiments.py`](../src/biocatalyst_quant/integrations/notion_experiments.py), [`test_notion_experiments.py`](../tests/unit/test_notion_experiments.py)

---

## DD-008 — `ARCHITECTURE_REVIEW.md` disposition
- **Date / decision ID**: 2026-10-20 / `DD-008`
- **Problem and source evidence**: It requires "exactly ten stocks", contradicting ADR-006 (`diff.md` #4).
- **Existing constraint / prior ADR**: ADR-006; user condition Q6 (do not delete or overwrite).
- **Option A / Option B**: **A** — add a `SUPERSEDED` banner with pointers, body untouched. **B** — delete or rewrite the review.
- **Expected advantage / cost / failure condition**: A keeps history; failure: a reader skips the banner — mitigated by placing it first.
- **Fastest distinguishing experiment**: `git diff` shows only added lines at the top.
- **User decision**: **APPROVED (Option A — Q6)**
- **Code/test links**: [`ARCHITECTURE_REVIEW.md`](ARCHITECTURE_REVIEW.md)
