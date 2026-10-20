# Testing & Validation Policy

## Test taxonomy

1. **Unit** (`tests/unit`): pure math, date eligibility, schemas, feature transforms. No network, disk or clock dependencies unless fake/injected.
2. **Integration** (`tests/integration`): document -> structured facts -> feature gate -> decision inputs, local test database/fixtures; deterministic, no real APIs.
3. **Contract** (add `tests/contract`): source payload schema changes; fixture replay; ensure adapter behavior and explicit missing fields.
4. **End-to-end/paper** (later): full historical replay against frozen sources; no live order submission.
5. **External smoke** (`@pytest.mark.external`): opt-in only, isolated and rate-limited; no CI secrets on untrusted PRs.
6. **Research evaluation** (separate): model calibration, temporal holdout, portfolio alpha, reality checks, block bootstrap; these are not substitutes for software tests.

## Mandatory adversarial tests

- A future result or revision must not enter a feature snapshot prior to its mode-resolved availability time (`historical_eligible_at` in replay, `live_available_at` live; vocabulary in `DATA_CONTRACTS.md`).
- A press release after exchange close must not transact at an earlier closing price.
- Ticker renaming, split and delisting must not drop a historical security.
- Multiple stories about one trial must not count as multiple independent outcomes.
- Date localization handles DST shifts; reject naive timestamps at boundaries.
- Clinical statistical extraction tests p-value decimal shifts, endpoint hierarchy, HR vs absolute risk, missing units, contradictory results.
- Zero volume, trading halts, partial fills, missing bars, invalid returns and high slippage must produce explicit results.
- Backtesting computes ten equal initial weights, rebalances on declared policy only, and accounts for fees on actual executed orders.

## Quantitative correctness

- Use hand-calculated toy examples for return and portfolio P&L, and independent reference implementations for complex calculations.
- For floating arithmetic use `pytest.approx`, with tolerances documented from numerical sensitivity.
- Add metamorphic/property tests where helpful (ordering invariance, partition invariance, monotonic cost penalty); adopt Hypothesis only after a specific need is shown.
- Golden files for extraction are event-separated into train/dev/test; do not tune prompts against test items.
- Report per-field exact-match/precision-recall, numeric-unit validation, provenance coverage, abstention rate, temporal violation rate, and cost/latency.

## CI gates

- Ruff formatting and lint: **zero errors**.
- mypy strict (`src/`): **zero errors**; exceptions require reviewed justification.
- Unit + deterministic integration coverage **>=85% branch-aware combined** as an initial floor; critical risk/point-in-time modules require 100% defined branch-case coverage, not a claim of total behavioral proof.
- External tests not on pull requests; isolate mock broker from production connections.
- Failed safety invariants always block merge; never waive a temporal data-leakage failure for coverage.

## Regression workflow

For every production bug: reproduce failing test, patch, then rerun targeted and full suites. Record dataset hash, code SHA, random seed, model/prompt version and decision clock for research regressions.
