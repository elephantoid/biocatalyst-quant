#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mode="${1:-full}"
if [[ "$mode" != "full" && "$mode" != "offline" ]]; then
  echo "Usage: bash scripts/quality.sh [full|offline]" >&2
  exit 2
fi
command -v uv >/dev/null || { echo "uv not installed" >&2; exit 1; }
test -f uv.lock || { echo "Missing uv.lock: run uv lock and commit it" >&2; exit 1; }
uv sync --locked
uv run --no-sync ruff format --check .
uv run --no-sync ruff check .
uv run --no-sync mypy src
uv run --no-sync pytest -m 'not external and not slow' --cov=biocatalyst_quant --cov-branch --cov-report=term-missing --cov-fail-under=85
uv run --no-sync bandit -q -r src
# Detect-secrets baseline must be generated and human-reviewed before use.
test -f .secrets.baseline || { echo 'Missing .secrets.baseline: run detect-secrets scan and review results' >&2; exit 1; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "Not a Git work tree: cannot enumerate files to scan" >&2; exit 1; }
# NUL-delimited end to end: a newline in a file name must not split or hide a path.
scan_list="$(mktemp)"
trap 'rm -f "$scan_list"' EXIT
git ls-files -z | { grep -zvE '^(uv\.lock|\.secrets\.baseline)$' || true; } > "$scan_list"
# An empty scan list would make detect-secrets-hook pass vacuously; treat it as failure.
test -s "$scan_list" || { echo "No tracked files to scan for secrets (stage files with git add)" >&2; exit 1; }
# Fail closed if the index lists a path that is not on disk (it would otherwise be skipped).
while IFS= read -r -d '' path; do
  test -e "$path" || { echo "Tracked path missing on disk, cannot scan: $path" >&2; exit 1; }
done < "$scan_list"
xargs -0 uv run --no-sync detect-secrets-hook --baseline .secrets.baseline < "$scan_list"
if [[ "$mode" == "full" ]]; then
  uv audit --locked
else
  echo 'OFFLINE MODE: vulnerability audit skipped; NOT a complete security pass.'
fi
echo "Local quality checks passed (${mode})."
