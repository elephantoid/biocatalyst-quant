# Notion Research Log — Official API Integration

**Decision:** Notion is the secondary *human-readable research notebook*, never the source of truth for training data, metrics, executed orders, or immutable lineage. The local experiment registry / verified artifacts remain authoritative.

## Setup
1. In Notion, create a dedicated page **BioCatalyst Quant / Experiments**.
2. Create a Notion **internal connection** with *read and insert content* capabilities; share that page with the connection.
3. Set `NOTION_TOKEN` and `NOTION_EXPERIMENTS_PAGE_ID` as local environment variables. Never commit tokens. This implementation uses `Notion-Version: 2026-03-11` and plain **child pages** under the parent page (not a Notion database/data source), avoiding schema migration concerns.
4. Create a local experiment directory with `manifest.json` and optionally `metrics.json`; run a dry run first.

```bash
export NOTION_TOKEN='YOUR_PRIVATE_NOTION_INTEGRATION_TOKEN'
export NOTION_EXPERIMENTS_PAGE_ID='YOUR_SHARED_PARENT_PAGE_ID'
python -m biocatalyst_quant.integrations.notion_experiments experiments/EXP-00042 --dry-run
python -m biocatalyst_quant.integrations.notion_experiments experiments/EXP-00042
```

Project must be installed / src on PYTHONPATH, e.g. `uv run python -m ...` in project root.

Example manifest:

```json
{
  "experiment_id": "EXP-00042",
  "status": "completed",
  "hypothesis": "Clinical features outperform price-only baseline",
  "data_snapshot": "snapshot-sha256-or-id",
  "feature_set": "F1",
  "model": "logistic-regression-baseline",
  "evaluation_protocol": "purged-walk-forward",
  "execution_assumptions": "5min, limit orders, 5min decision delay",
  "code_commit": "git-sha",
  "decision": "rejected",
  "limitations": "insufficient delisted security coverage"
}
```

## Operation and correctness
- Run sync **after** local validation / atomic publication marks an experiment `completed`; it must **not** block experiment completion or mutate its metrics. Failures go into a retriable outbox/sync log (recommended integration task; prototype CLI returns a failure for external orchestration to retry).
- Each completed manifest revision is published to a uniquely named immutable child page: `EXPERIMENT_ID | SHA256(prefix)`. Same title is detected by listing child pages before create; reruns normally skip duplicates.
- Notion is not transactionally coupled to local artifacts. A concurrent publisher, ambiguous API write failure, or externally renamed page can still cause duplicates. Use a **single Notion sync writer** and periodic reconciliation. Future hardening: durable outbox and Notion reconciliation indexes.
- Publish only **whitelisted metadata and summary metrics**. Do not upload licensed vendor data, restricted news full text, secrets, research source PDFs, or order/execution raw artifacts. Link to secured storage only when permitted.
- Keep rejected/failed scientific experiments in local registry. This publisher accepts `completed` runs including rejected hypotheses; it does not publish interrupted computational runs.
- Keep `experiment_id`, metric definitions, baselines, OOS fold definition, costs, leakage checks, decision, and limitations available in the manifest. Replace unrecorded placeholders before relying on Notion summaries.
- Notion rate limiting: handle HTTP 429/529, honor `Retry-After`. Do not blindly retry ambiguous writes after a 503; first read/reconcile remote state. Docs: https://developers.notion.com/reference/request-limits

## Why pages, not a database?
A simple parent-page + child-page archive is the first vertical slice. A Notion **data source** with filterable status, strategy, horizon, or hypothesis properties is a **conditional upgrade** once experiment volume and review workflows justify schema administration. Newer Notion API versions separate databases from data sources.

## Acceptance tests
- Dry run performs no API calls and prints digest/title.
- Same experiment and summary has stable digest and page name.
- A repeated sync skips the page if it exists remotely.
- Changed validated summary creates a new revision page, never overwrites an old page.
- Missing token/permissions/parent ID reports an actionable error; local results remain untouched.
- API retries bounded for rate limiting; published documents exclude non-whitelisted fields.
