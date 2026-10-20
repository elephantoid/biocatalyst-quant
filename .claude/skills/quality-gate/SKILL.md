---
name: quality-gate
description: Run appropriate local quality checks
---
# quality-gate

Before checks, verify local environment and uv.lock. During coding run focused tests; before release run `bash scripts/quality.sh full` (network needed). Never present `offline` as security complete. Summarize actual results and blockers, including inability to audit vulnerabilities offline.
