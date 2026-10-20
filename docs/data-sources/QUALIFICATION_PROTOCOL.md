# Data Source Qualification Protocol

## Fixture sample (20–30 events initially)
Include: successful and failed trials; low-impact events; delisted firms; reverse splits; ticker changes; premarket and afterhours press releases; simultaneous/confounded disclosures; halts; zero-volume bars; conference embargoes and revised expected dates. Sample historically eligible companies, not just famous winners.

## Checklist per source
- Endpoint, access method, credentials, rate limits, license for local retention / research / automated execution.
- Raw historical coverage start/end; timezone and DST; time precision; first-available-as-of proof.
- Delisted securities, historical ticker/identity aliases and action adjustments.
- Extended-hours 5m volume and possible VWAP; missing and no-trade intervals.
- Retrieval accuracy vs at least one independent source, date revision behavior, errors and retry behavior.
- License and expected budget; provider version and audit trail.

## Results
Use `status: unverified | trial | qualified | rejected`; attach dated retrieval log, sample IDs, failed cases, numerical missingness and scorecard. A provider is not qualified simply because its marketing page advertises 5m bars.
