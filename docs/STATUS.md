# STATUS

Project: BioCatalyst Quant — Reproducible Research
Date: 2026-10-20
Mode: **RECONCILIATION COMPLETE — AWAITING TASK APPROVAL** (no new core feature work started)
Branch: `chore/sync-reconciliation` (no commits yet; files staged, not committed)
Approved task: none. Proposed next: `B1-01` (see end).

Severity labels: **CONFLICT** accepted ADR vs code · **MISSING** planned, not built · **QUALITY ISSUE** failed gate · **OPEN** needs user decision. Decisions: `DD-003`~`DD-008` in [`DESIGN_DECISIONS.md`](DESIGN_DECISIONS.md).

## Quality gates (measured 2026-10-20, `bash scripts/quality.sh full`, exit 0)
| Gate | Result |
|---|---|
| `ruff format --check .` | PASS (49 files) |
| `ruff check .` | PASS |
| `mypy src` (strict) | PASS (4 files) |
| `pytest -m 'not external and not slow'` + branch coverage | PASS — 61 passed, 98.01% (min 85%) |
| `bandit -q -r src` | PASS — two line-scoped `# nosec` (B311 jitter, B310 `urlopen`), reviewed in `DD-006` |
| `detect-secrets` vs `.secrets.baseline` | PASS — baseline has 0 findings |
| `uv audit --locked` (online) | PASS — no known vulnerabilities, 36 packages |
Before this work: ruff 1 error (PT018), mypy 1 error (`no-any-return`), no `.secrets.baseline`, 0 tracked files. `pre-commit` hooks (pre-commit, pre-push) are installed locally and ran on every commit, including the new `no-local-paths` hook.

## Evidence-backed state
- **Governance & specs**: implemented (`AGENTS.md`, `CLAUDE.md`, `PROJECT_SPEC.md`, `ACCEPTANCE.md`, `BACKLOG.md`). Local-only, git-ignored under `local-docs/`: `BUILD_PROMPT.md`, `architecture-map.html`, `agent/` (Antigravity prompts). The one-off audit `diff.md` moved there too; its findings are carried by `DESIGN_DECISIONS.md` (DD-001~008).
- **ADR-001~008**: all present; hashes re-verified (`ADR-INTEGRATION.md`). ADR-005 revised to v1.1, v1.0 preserved.
- **Temporal vocabulary**: fixed in docs (`DD-004`). Code (`domain.py`, single `available_at`) not yet aligned: **MISSING** → `B1-01`.
- **Domain code**: `HistoricalFeature`, `is_available`, `equal_weight_return` only. **CONFLICT**: `equal_weight_return` requires exactly 10 returns (ADR-006: max 10, 10% per new slot, rest cash). Deliberately left unchanged → `B5-01`, test-first.
- **Notion export** (`integrations/notion_experiments.py`): passes all gates; dedupe, ambiguous-write reconcile, bounded retries done. Sync-status separation **partial**; outbox deferred to B7 (`DD-007`).
- **B1~B7 core modules**: **MISSING** (not approved).
- **Environment**: `.git` exists (0 commits, no remote), `uv.lock` (37 packages), `.venv` Python 3.12.13, `.secrets.baseline` created. No local data or prior artifacts were deleted.

## OPEN questions
1. ADR-005 window length, step size, embargo width.
2. ADR-007 (lineage/indexing) is direction-only.
3. `DD-002` (B1-01 Option A vs B) is PENDING; must be re-based on `DD-004` vocabulary.
4. Bandit B310 residual risk: urllib redirect may forward `Authorization` — fix or accept (`DD-006`). (`parent_id` validation and metrics whitelist were fixed; title-match trust accepted until the B7 outbox, `DD-007`.)
5. External data providers: all `unverified` (`data-sources/DATA_SOURCE_REGISTRY.md`).
6. First commit: not requested yet. When requested, it must be on a work branch, never `main`.

## Next start point
`B1-01` — see [`DESIGN_DECISIONS.md`](DESIGN_DECISIONS.md) `DD-002` (needs approval of Option A/B and the `DD-004` vocabulary).
