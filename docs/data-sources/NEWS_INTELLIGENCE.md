# News Intelligence Policy

Three layers: **primary disclosure** (company IR, wire, SEC, FDA, conference), **specialist commentary** (Fierce, STAT, Endpoints, BioPharma Dive), and **future-event discovery** (calendars and GDELT). Never treat a later rewrite as the first release automatically.

Preserve document source URL/id, document hash, provider-reported publication, observed_at, license, attribution and any amended/corrected version. Link every announcement to an event and optionally a `information_update_id` and `information_cluster_id`. Store newly announced facts separately from reused facts. Keep market reaction after disclosure as target/label, not earlier prediction feature.

Prioritize IR + GlobeNewswire + SEC; conference schedules (ASCO/AACR) and FDA; then specialist publications; then GDELT/calendars. Before expanding, compare **incremental coverage**, timestamps, retrieval false negatives, cost and permissible storage. A news report may precede or follow the originating IR or filing: check, do not infer causality from proximity.
