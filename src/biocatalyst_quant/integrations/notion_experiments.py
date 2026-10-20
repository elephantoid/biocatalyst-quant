"""Publish immutable experiment summaries to Notion using its official REST API.

Local experiment artifacts are always authoritative. Notion is a human-readable mirror.
No third-party dependencies. Network I/O happens ONLY on explicit CLI invocation.

Sync outcome is reported separately from experiment completion: a Notion failure never
touches local artifacts and never changes the experiment's own ``completed`` status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
from math import isfinite
from pathlib import Path
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

API = "https://api.notion.com/v1"
NOTION_VERSION = "2026-03-11"
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
# Notion page IDs: 32 hex digits, optionally dashed as a UUID.
PAGE_ID = re.compile(
    r"^[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}$"
)
# Only these summary metrics are mirrored; extend deliberately, never by passing the file through.
ALLOWED_METRIC_KEYS = frozenset(
    {
        "auc",
        "brier",
        "cagr",
        "hit_rate",
        "log_loss",
        "max_drawdown",
        "n_events",
        "n_trades",
        "sharpe",
        "sortino",
        "turnover",
    }
)
MAX_METRIC_TEXT = 200
MAX_ATTEMPTS = 5
RECONCILE_ATTEMPTS = 3
MAX_RETRY_DELAY_SECONDS = 60.0


class NotionSyncError(RuntimeError):
    """A Notion sync failed in a way that is safe to retry later."""


class NotionAmbiguousWriteError(NotionSyncError):
    """A create request may or may not have been applied remotely."""


class NotionClient(Protocol):
    """Minimal surface used by :func:`sync`; allows offline fakes in tests."""

    def find_child_page(self, parent_id: str, title: str) -> dict[str, Any] | None: ...

    def call(
        self, method: str, endpoint: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]: ...


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )


def rich(text: str) -> dict[str, Any]:
    return {"type": "text", "text": {"content": text[:2000]}}


def paragraph(label: str, value: Any) -> dict[str, Any]:
    value_str = (
        json.dumps(value, ensure_ascii=False, sort_keys=True)
        if not isinstance(value, str)
        else value
    )
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [rich(f"{label}: {value_str}")]},
    }


def validate_page_id(page_id: str) -> str:
    """Reject anything that is not a Notion page ID before it reaches a URL path."""
    if not PAGE_ID.fullmatch(page_id):
        raise ValueError("Notion parent page ID must be a 32-hex-digit (optionally dashed) ID")
    return page_id


def whitelist_metrics(raw: Any) -> dict[str, Any]:
    """Keep only known keys with finite scalar values; reject (never silently drop) the rest."""
    if not isinstance(raw, dict):
        raise ValueError("metrics.json must be a JSON object")
    unknown = sorted(str(key) for key in raw if key not in ALLOWED_METRIC_KEYS)
    if unknown:
        raise ValueError(f"metrics.json has keys that are not allowed to be mirrored: {unknown}")
    for key, value in raw.items():
        if isinstance(value, bool) or not isinstance(value, int | float | str):
            raise ValueError(f"metric {key!r} must be a number or short string")
        if isinstance(value, float) and not isfinite(value):
            raise ValueError(f"metric {key!r} must be finite")
        if isinstance(value, str) and len(value) > MAX_METRIC_TEXT:
            raise ValueError(f"metric {key!r} text exceeds {MAX_METRIC_TEXT} characters")
    return dict(raw)


def manifest_summary(folder: Path) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    """Whitelist fields. Do not mirror raw data, model weights, or secrets."""
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    metrics_path = folder / "metrics.json"
    metrics = (
        whitelist_metrics(json.loads(metrics_path.read_text(encoding="utf-8")))
        if metrics_path.exists()
        else {}
    )
    experiment_id = manifest.get("experiment_id")
    if not isinstance(experiment_id, str) or not IDENTIFIER.fullmatch(experiment_id):
        raise ValueError("manifest.json requires a safe experiment_id")
    if manifest.get("status") != "completed":
        raise ValueError("Only completed experiments may be published")
    sections = {
        "hypothesis": manifest.get("hypothesis", "not recorded"),
        "decision": manifest.get("decision", "not recorded"),
        "data_snapshot": manifest.get("data_snapshot", "not recorded"),
        "feature_set": manifest.get("feature_set", "not recorded"),
        "model": manifest.get("model", "not recorded"),
        "evaluation_protocol": manifest.get("evaluation_protocol", "not recorded"),
        "execution_assumptions": manifest.get("execution_assumptions", "not recorded"),
        "code_commit": manifest.get("code_commit", "not recorded"),
        "limitations": manifest.get("limitations", "not recorded"),
        "metrics": metrics,
    }
    # Hash only what is mirrored. Amendments produce a new Notion page, never silent edits.
    digest = hashlib.sha256(
        canonical_bytes({"experiment_id": experiment_id, **sections})
    ).hexdigest()
    title = f"{experiment_id} | {digest[:12]}"
    blocks = [paragraph("Experiment ID", experiment_id), paragraph("Summary SHA256", digest)]
    for key, value in sections.items():
        encoded = (
            json.dumps(value, ensure_ascii=False, sort_keys=True)
            if not isinstance(value, str)
            else value
        )
        # Split long text to respect Notion 2000-character rich-text limit.
        for idx in range(0, max(len(encoded), 1), 1700):
            blocks.append(
                paragraph(key if idx == 0 else f"{key} (cont.)", encoded[idx : idx + 1700])
            )
    if len(blocks) > 100:
        raise ValueError("Summary too large for a single page creation; store details locally")
    return title, {"experiment_id": experiment_id, "digest": digest, "sections": sections}, blocks


def _jitter() -> float:
    # Retry jitter only; not security-sensitive, so a non-cryptographic PRNG is appropriate.
    return random.random() / 4  # nosec B311


def retry_delay(retry_after: str | None, attempt: int) -> float:
    """Seconds to wait: honour a numeric Retry-After, else bounded exponential backoff."""
    if retry_after:
        try:
            return min(max(float(retry_after), 0.0), MAX_RETRY_DELAY_SECONDS)
        except ValueError:
            pass  # HTTP-date form is not supported; fall back to backoff.
    # `1 << attempt` keeps the type `int`; `2**attempt` is typed `Any` for a non-literal exponent.
    return float(min(1 << attempt, 30)) + _jitter()


class NotionAPI:
    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("NOTION_TOKEN is required")
        self.token = token

    def call(
        self, method: str, endpoint: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = API + endpoint
        # urlopen also accepts file:/ and custom schemes; refuse anything but fixed HTTPS.
        if not url.startswith("https://api.notion.com/"):
            raise NotionSyncError("Refusing to call a non-Notion HTTPS endpoint")
        data = canonical_bytes(payload) if payload is not None else None
        idempotent = method == "GET"
        retryable = {429, 529, 500, 502, 503, 504} if idempotent else {429, 529}
        for attempt in range(MAX_ATTEMPTS):
            request = Request(
                url,
                data=data,
                method=method,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Notion-Version": NOTION_VERSION,
                    "Content-Type": "application/json",
                },
            )
            try:
                # URL is the fixed https://api.notion.com/ origin checked above.
                with urlopen(request, timeout=30) as response:  # nosec B310
                    body = json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                if exc.code in retryable and attempt < MAX_ATTEMPTS - 1:
                    # 429/529 mean the write was not applied, so a retry cannot duplicate it.
                    time.sleep(retry_delay(exc.headers.get("Retry-After"), attempt))
                    continue
                detail = exc.read(300).decode("utf-8", errors="replace")
                message = f"Notion API HTTP {exc.code}: {detail}"
                if not idempotent and exc.code >= 500:
                    raise NotionAmbiguousWriteError(message) from exc
                raise NotionSyncError(message) from exc
            except (URLError, TimeoutError, ValueError) as exc:
                # A POST may have been applied before the failure; the caller must reconcile.
                if not idempotent:
                    raise NotionAmbiguousWriteError(
                        "Notion write outcome unknown; reconcile before any new create"
                    ) from exc
                raise NotionSyncError("Notion request failed; rerun sync later") from exc
            if not isinstance(body, dict):
                raise NotionSyncError("Unexpected Notion response shape")
            return body
        raise NotionSyncError("Notion API retry limit reached")

    def find_child_page(self, parent_id: str, title: str) -> dict[str, Any] | None:
        parent_id = quote(validate_page_id(parent_id), safe="")
        cursor: str | None = None
        while True:
            params: dict[str, str | int] = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor
            result = self.call("GET", f"/blocks/{parent_id}/children?{urlencode(params)}")
            for block in result.get("results", []):
                if (
                    isinstance(block, dict)
                    and block.get("type") == "child_page"
                    and block.get("child_page", {}).get("title") == title
                ):
                    return block
            if not result.get("has_more"):
                return None
            next_cursor = result.get("next_cursor")
            if not isinstance(next_cursor, str) or not next_cursor:
                raise NotionSyncError("Notion pagination cursor missing")
            cursor = next_cursor


def sync(
    folder: Path, parent_id: str, api: NotionClient | None, dry_run: bool = False
) -> dict[str, str]:
    title, summary, blocks = manifest_summary(folder)
    if dry_run:
        return {"status": "dry-run", "title": title, "digest": summary["digest"]}
    if api is None:
        raise ValueError("A Notion client is required unless dry_run is set")
    found = api.find_child_page(parent_id, title)
    if found:
        return {"status": "already-published", "page_id": found["id"], "title": title}
    # Single writer recommended. Do not concurrently sync the same experiment.
    try:
        response = api.call(
            "POST",
            "/pages",
            {
                "parent": {"type": "page_id", "page_id": parent_id},
                "properties": {"title": {"type": "title", "title": [rich(title)]}},
                "children": blocks,
            },
        )
    except NotionAmbiguousWriteError as exc:
        # Never re-POST after an ambiguous failure: look the page up by its
        # experiment_id + summary-hash title instead (bounded attempts).
        for attempt in range(RECONCILE_ATTEMPTS):
            time.sleep(min(2**attempt, 8))
            found = api.find_child_page(parent_id, title)
            if found:
                return {
                    "status": "published-after-reconcile",
                    "page_id": found["id"],
                    "title": title,
                }
        raise NotionSyncError(
            "Notion write outcome unknown and page not found after reconcile; "
            "rerun sync to reconcile remote pages"
        ) from exc
    page_id = response.get("id")
    if not isinstance(page_id, str):
        raise NotionSyncError("Notion create response missing page id; rerun sync to reconcile")
    return {"status": "published", "page_id": page_id, "title": title}


def display_path(path: str | Path | None) -> str:
    """Show a path relative to the working directory; outside it, only the file name."""
    if path is None:
        return "<unknown>"
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return candidate.name


def _report_failure(error: str) -> int:
    # Sync state is separate from experiment state: local artifacts are untouched.
    failure = {"sync_status": "failed", "error": error, "local_artifacts": "untouched"}
    print(json.dumps(failure, ensure_ascii=False, indent=2), file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish completed experiment summary to Notion")
    parser.add_argument("experiment_dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    parent_id = os.environ.get("NOTION_EXPERIMENTS_PAGE_ID", "")
    token = os.environ.get("NOTION_TOKEN", "")
    if not args.dry_run:
        if not parent_id:
            parser.error("Set NOTION_EXPERIMENTS_PAGE_ID to a shared Notion page ID")
        try:
            validate_page_id(parent_id)
        except ValueError as exc:
            parser.error(str(exc))
        if not token:
            parser.error("Set NOTION_TOKEN to a Notion integration token")
    try:
        result = sync(
            args.experiment_dir,
            parent_id,
            None if args.dry_run else NotionAPI(token),
            args.dry_run,
        )
    except OSError as exc:
        # str(OSError) embeds the absolute path; report a project-relative one instead.
        return _report_failure(f"{type(exc).__name__}: cannot read {display_path(exc.filename)}")
    except (NotionSyncError, ValueError) as exc:
        return _report_failure(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
