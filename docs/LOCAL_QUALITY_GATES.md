# Local-first quality gates

## Goal

GitHub Actions usage is exhausted: this project relies on **local** gates. A pre-push hook protects ordinary pushes but can be bypassed (`--no-verify`), so use `bash scripts/quality.sh full` before any deployment or live trading change.

## Bootstrap (one-time; needs internet)

```bash
uv lock
uv sync --locked
uv run detect-secrets scan > .secrets.baseline
uv run detect-secrets audit .secrets.baseline   # review all detected entries; never approve real secrets
uv run pre-commit install --hook-type pre-commit --hook-type pre-push
```

Review the baseline before committing it. `uv.lock` must be committed. Keep secret values outside version control. Initial hook environments (remote repositories) also require a network connection.

## Day-to-day

```bash
uv run pre-commit run --all-files                 # fast stage
uv run pre-commit run --hook-stage pre-push --all-files
bash scripts/quality.sh full                      # full local release check
bash scripts/quality.sh offline                   # clearly incomplete security audit
```

`pre-commit` runs formatting/lint, file hygiene, secret scanning, and quick unit tests. `pre-push` runs strict typing, integration/unit tests with branch coverage, Bandit, and `uv audit` (online only). Manual runs the full gate. A network failure causes the full gate to fail, not silently pass.

## Testing policy

- Unit tests are fast, deterministic, offline, with no real data/services.
- Integration tests cover database adapters, serialization, ingestion, point-in-time joins, event deduplication and replay using fixtures.
- External/end-to-end tests require explicit credentials and are opt-in; excluded from normal gates.
- Branch coverage >=85% is a repository minimum, **not** proof of correctness.
- Mandatory domain invariants: no future timestamps in features; tickers and corporate actions as of trade date; no duplicated event IDs; weights sum to 1 at rebalance; no fills before release; accounting remains balanced.
- Add property-based tests (Hypothesis) when implementing returns, time ordering, weight normalization, and bitemporal logic; use mutation tests periodically to probe assertion strength.
- Every production defect gets a regression test.

## Security policy

- Ruff: code hygiene, not vulnerability auditing.
- Bandit: Python source security heuristics; review false positives rather than globally silencing warnings.
- detect-secrets: checks newly added credentials against an auditable baseline; a baseline is not permission to commit a genuine secret.
- `uv audit`: dependency vulnerabilities and adverse package statuses; **requires network**, and is not an SBOM, license audit, or all-purpose supply-chain scanner.
- Dependencies must be locked; prefer reviewed release updates, and re-audit after updates.
- Planned expansion only when justified: license allowlist / SBOM generation, OS/containers scan, signed releases, SAST, trading-key isolation.

## Failure & enforcement

- Do not use `SKIP=...` or `--no-verify` to merge a known failure except under written exception approval with owner and expiration.
- Local Git hooks cannot enforce policy for all contributors or protect the remote branch by themselves. Offline audit is an explicit **partial pass**, never a complete pass.
- Store command outputs in local, git-ignored artifacts for audit trails where needed.
- For real capital deployment, use an independent manual go/no-go checklist and risk limit controls; passing tests is not proof of strategy profitability.
