# Data Contracts — first draft

## Universal timestamp contract

Canonical vocabulary (user decision 2026-10-20, `DD-004`; consistent with ADR-001):

| Field | Meaning |
|---|---|
| `event_at` | When the real-world event actually happened |
| `published_at` | When public disclosure is confirmed to have occurred |
| `observed_at` | When our system first discovered the item |
| `ingested_at` | When the original was durably stored (distinct from `observed_at`) |
| `historical_eligible_at` | Conservative time a **historical simulation** may use the information |
| `live_available_at` | Time the information became usable in the **live** system after validation, from measured pipeline logs |
| `decision_at` | Investment decision time |

- Persist all instants as timezone-aware UTC. Keep the source timezone and timestamp precision (e.g. date-only vs second) alongside when the source provides them.
- Availability depends on mode: `historical_eligible_at` in replay, `live_available_at` in live operation. Never default either to `published_at`; if the evidence is missing, mark it unknown.
- `event_at` may predate publication; only a **validated** availability time (per mode) can permit feature consumption: `availability <= decision_at`.
- `historical_eligible_at` is reconstructed from contemporaneous publication evidence plus conservative processing assumptions; keep it distinct from the measured `observed_at` / `ingested_at` / `live_available_at`.
- Never change historical availability because a record was revised or fetched today. Store every version and derivation.
- Code status: `domain.py` still carries a single legacy `available_at` field. Renaming/splitting it is task `B1-01` (not yet approved); until then treat `available_at` in this repo as the mode-resolved availability time above.

## Feature record

Required: `feature_id`, `security_id`, `event_id?`, `feature_name`, `feature_value`, `feature_unit`, `available_at` (mode-resolved; see above), `availability_mode?`, `source_id`, `source_hash`, `extractor_version`, `validation_status`.

Allowed status: `validated`, `rejected`, `unknown`, `needs_review`. Only `validated` can enter production feature views. Schema-valid and fact-valid are independent conditions.

## Event record

Required: stable `event_id`, `NCT_ID?`, `CIK?`, `drug_id?`, `indication_id?`, `event_type`, `outcome?`, evidence links and separate source publication timestamps. Link duplicate media reports to one event; retain the earliest trustworthy release and all revisions.

## Decision and order record

Required: decision time, data snapshot hash, model & config version, eligible universe, selected ten securities (or explicitly recorded shortage), target weights, actionable quoted price/time, executed price/volume/fees/slippage, and reasons for rejection/replacement.
