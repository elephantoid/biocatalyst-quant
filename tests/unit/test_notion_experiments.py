import json
from email.message import Message
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

import pytest

from biocatalyst_quant.integrations import notion_experiments as ne
from biocatalyst_quant.integrations.notion_experiments import (
    NotionAmbiguousWriteError,
    NotionAPI,
    NotionSyncError,
    manifest_summary,
    sync,
    validate_page_id,
    whitelist_metrics,
)

# Dummy sequential ID for tests, not a credential.
PARENT = "0123456789abcdef0123456789abcdef"  # pragma: allowlist secret


def make_experiment(tmp_path: Path, experiment_id: str = "EXP-1", **extra: Any) -> Path:
    path = tmp_path / experiment_id
    path.mkdir()
    manifest = {"experiment_id": experiment_id, "status": "completed", **extra}
    (path / "manifest.json").write_text(json.dumps(manifest))
    return path


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def http_error(code: int, retry_after: str | None = None) -> HTTPError:
    headers = Message()
    if retry_after is not None:
        headers["Retry-After"] = retry_after
    return HTTPError("https://api.notion.com/v1/x", code, "err", headers, BytesIO(b"detail"))


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    recorded: list[float] = []
    monkeypatch.setattr(ne.time, "sleep", recorded.append)
    return recorded


def script_urlopen(monkeypatch: pytest.MonkeyPatch, outcomes: list[bytes | Exception]) -> list[Any]:
    """Replace urlopen with scripted outcomes; returns the list of Requests seen."""
    seen: list[Any] = []
    queue = list(outcomes)

    def fake(request: Any, timeout: float) -> FakeResponse:
        seen.append(request)
        outcome = queue.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return FakeResponse(outcome)

    monkeypatch.setattr(ne, "urlopen", fake)
    return seen


def test_deterministic_title_and_revision(tmp_path: Path) -> None:
    path = make_experiment(tmp_path, hypothesis="a", secret="SHOULD_NOT_PUBLISH")
    first, _summary, blocks = manifest_summary(path)
    assert first == manifest_summary(path)[0]
    assert "SHOULD_NOT_PUBLISH" not in json.dumps(blocks)
    assert sync(path, "", None, dry_run=True)["title"] == first
    (path / "metrics.json").write_text('{"sharpe": 1.2}')
    assert manifest_summary(path)[0] != first


@pytest.mark.parametrize(
    "page_id",
    [
        "",
        "parent",
        "../x",
        PARENT[:-1],
        PARENT + "/children",
        PARENT + "?x=1",
    ],
)
def test_page_id_rejects_non_ids_before_any_request(
    monkeypatch: pytest.MonkeyPatch, page_id: str
) -> None:
    seen = script_urlopen(monkeypatch, [])
    with pytest.raises(ValueError, match="page ID"):
        NotionAPI("tok").find_child_page(page_id, "T")
    assert seen == []


def test_page_id_accepts_dashed_uuid() -> None:
    dashed = "01234567-89ab-cdef-0123-456789abcdef"
    assert validate_page_id(dashed) == dashed


def test_metrics_are_whitelisted_and_scalar(tmp_path: Path) -> None:
    path = make_experiment(tmp_path)
    (path / "metrics.json").write_text('{"sharpe": 1.2, "n_trades": 40, "hit_rate": "0.55"}')
    _title, summary, _blocks = manifest_summary(path)
    assert summary["sections"]["metrics"] == {"sharpe": 1.2, "n_trades": 40, "hit_rate": "0.55"}


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ([1, 2], "JSON object"),
        ({"api_key": "x"}, "not allowed"),
        ({"sharpe": {"nested": 1}}, "number or short string"),
        ({"sharpe": [1]}, "number or short string"),
        ({"sharpe": True}, "number or short string"),
        ({"sharpe": float("inf")}, "finite"),
        ({"sharpe": "x" * 201}, "exceeds"),
    ],
)
def test_metrics_rejections(raw: Any, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        whitelist_metrics(raw)


def test_metrics_file_with_unknown_key_blocks_publication(tmp_path: Path) -> None:
    path = make_experiment(tmp_path)
    (path / "metrics.json").write_text('{"sharpe": 1, "raw_prices": [1, 2, 3]}')
    with pytest.raises(ValueError, match="not allowed"):
        sync(path, PARENT, FakeAPI())


class FakeAPI:
    def __init__(self) -> None:
        self.pages: dict[str, dict[str, Any]] = {}
        self.creates = 0

    def find_child_page(self, parent_id: str, title: str) -> dict[str, Any] | None:
        return self.pages.get(title)

    def call(
        self, method: str, endpoint: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        assert payload is not None
        self.creates += 1
        title = payload["properties"]["title"]["title"][0]["text"]["content"]
        self.pages[title] = {"id": "page-one"}
        return {"id": "page-one"}


def test_remote_idempotency(tmp_path: Path) -> None:
    path = make_experiment(tmp_path, "EXP-2")
    api = FakeAPI()
    assert sync(path, "parent", api)["status"] == "published"
    assert sync(path, "parent", api)["status"] == "already-published"
    assert api.creates == 1


def test_sync_requires_client_unless_dry_run(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Notion client"):
        sync(make_experiment(tmp_path), "parent", None)


@pytest.mark.parametrize(
    ("manifest", "message"),
    [
        ({"experiment_id": "../evil", "status": "completed"}, "safe experiment_id"),
        ({"experiment_id": "EXP-3", "status": "running"}, "completed"),
        (
            {
                "experiment_id": "EXP-3",
                "status": "completed",
                "notes": 1,
                "hypothesis": "x" * 400_000,
            },
            "too large",
        ),
    ],
)
def test_manifest_rejections(tmp_path: Path, manifest: dict[str, Any], message: str) -> None:
    path = tmp_path / "bad"
    path.mkdir()
    (path / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match=message):
        manifest_summary(path)


def test_long_text_is_split_into_continuation_blocks(tmp_path: Path) -> None:
    path = make_experiment(tmp_path, "EXP-4", hypothesis="y" * 3500)
    _title, _summary, blocks = manifest_summary(path)
    labels = [b["paragraph"]["rich_text"][0]["text"]["content"] for b in blocks]
    assert any(label.startswith("hypothesis (cont.):") for label in labels)


def test_retry_delay_bounds() -> None:
    assert ne.retry_delay("3", 0) == 3.0
    assert ne.retry_delay("-5", 0) == 0.0
    assert ne.retry_delay("999999", 0) == ne.MAX_RETRY_DELAY_SECONDS
    assert 4.0 <= ne.retry_delay("Wed, 21 Oct 2026 07:28:00 GMT", 2) < 4.25
    assert 1.0 <= ne.retry_delay(None, 0) < 1.25


def test_token_required() -> None:
    with pytest.raises(ValueError, match="NOTION_TOKEN"):
        NotionAPI("")


def test_call_success_sends_whitelisted_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = script_urlopen(monkeypatch, [b'{"id": "p"}'])
    assert NotionAPI("tok").call("POST", "/pages", {"a": 1}) == {"id": "p"}
    assert seen[0].get_header("Authorization") == "Bearer tok"
    assert seen[0].get_header("Notion-version") == ne.NOTION_VERSION


def test_call_refuses_non_notion_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ne, "API", "file:///etc")
    with pytest.raises(NotionSyncError, match="non-Notion"):
        NotionAPI("tok").call("GET", "/passwd")


def test_post_retries_rate_limit_then_succeeds(
    monkeypatch: pytest.MonkeyPatch, sleeps: list[float]
) -> None:
    seen = script_urlopen(monkeypatch, [http_error(429, "0"), b'{"id": "p"}'])
    assert NotionAPI("tok").call("POST", "/pages", {}) == {"id": "p"}
    assert len(seen) == 2
    assert sleeps == [0.0]


def test_get_retries_server_error_but_is_bounded(
    monkeypatch: pytest.MonkeyPatch, sleeps: list[float]
) -> None:
    seen = script_urlopen(monkeypatch, [http_error(503) for _ in range(ne.MAX_ATTEMPTS)])
    with pytest.raises(NotionSyncError, match="HTTP 503") as info:
        NotionAPI("tok").call("GET", "/x")
    assert not isinstance(info.value, NotionAmbiguousWriteError)
    assert len(seen) == ne.MAX_ATTEMPTS
    assert len(sleeps) == ne.MAX_ATTEMPTS - 1


def test_post_client_error_is_not_ambiguous(monkeypatch: pytest.MonkeyPatch) -> None:
    script_urlopen(monkeypatch, [http_error(400)])
    with pytest.raises(NotionSyncError, match="HTTP 400") as info:
        NotionAPI("tok").call("POST", "/pages", {})
    assert not isinstance(info.value, NotionAmbiguousWriteError)


@pytest.mark.parametrize(
    "failure", [http_error(503), URLError("reset"), TimeoutError(), ValueError("bad json")]
)
def test_post_uncertain_failures_are_ambiguous(
    monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    seen = script_urlopen(monkeypatch, [failure])
    with pytest.raises(NotionAmbiguousWriteError):
        NotionAPI("tok").call("POST", "/pages", {})
    assert len(seen) == 1  # no blind re-POST


def test_get_transport_failure_is_retryable_sync_error(monkeypatch: pytest.MonkeyPatch) -> None:
    script_urlopen(monkeypatch, [URLError("down")])
    with pytest.raises(NotionSyncError) as info:
        NotionAPI("tok").call("GET", "/x")
    assert not isinstance(info.value, NotionAmbiguousWriteError)


def test_non_object_response_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    script_urlopen(monkeypatch, [b"[1]"])
    with pytest.raises(NotionSyncError, match="response shape"):
        NotionAPI("tok").call("GET", "/x")


def test_rate_limit_exhaustion_on_post(
    monkeypatch: pytest.MonkeyPatch, sleeps: list[float]
) -> None:
    script_urlopen(monkeypatch, [http_error(429, "0") for _ in range(ne.MAX_ATTEMPTS)])
    with pytest.raises(NotionSyncError, match="HTTP 429"):
        NotionAPI("tok").call("POST", "/pages", {})


def test_find_child_page_paginates(monkeypatch: pytest.MonkeyPatch) -> None:
    page1 = {"results": [{"type": "paragraph"}], "has_more": True, "next_cursor": "c1"}
    page2 = {
        "results": [{"type": "child_page", "id": "z", "child_page": {"title": "T"}}],
        "has_more": False,
    }
    seen = script_urlopen(monkeypatch, [json.dumps(page1).encode(), json.dumps(page2).encode()])
    found = NotionAPI("tok").find_child_page(PARENT, "T")
    assert found is not None
    assert found["id"] == "z"
    assert "start_cursor=c1" in seen[1].full_url


def test_find_child_page_absent_and_missing_cursor(monkeypatch: pytest.MonkeyPatch) -> None:
    script_urlopen(monkeypatch, [b'{"results": [], "has_more": false}'])
    assert NotionAPI("tok").find_child_page(PARENT, "T") is None
    script_urlopen(monkeypatch, [b'{"results": [], "has_more": true}'])
    with pytest.raises(NotionSyncError, match="cursor"):
        NotionAPI("tok").find_child_page(PARENT, "T")


class AmbiguousAPI:
    """First create is applied remotely but its response is lost."""

    def __init__(self, visible_after: int) -> None:
        self.visible_after = visible_after
        self.lookups = 0
        self.creates = 0

    def find_child_page(self, parent_id: str, title: str) -> dict[str, Any] | None:
        self.lookups += 1
        # lookup #1 is the pre-create dedupe check; later lookups are reconciliation.
        return {"id": "page-late"} if self.lookups > self.visible_after else None

    def call(
        self, method: str, endpoint: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self.creates += 1
        raise NotionAmbiguousWriteError("lost response")


def test_ambiguous_write_reconciles_without_second_create(
    tmp_path: Path, sleeps: list[float]
) -> None:
    api = AmbiguousAPI(visible_after=2)
    result = sync(make_experiment(tmp_path), "parent", api)
    assert result["status"] == "published-after-reconcile"
    assert result["page_id"] == "page-late"
    assert api.creates == 1


def test_ambiguous_write_unresolved_fails_with_bounded_lookups(
    tmp_path: Path, sleeps: list[float]
) -> None:
    api = AmbiguousAPI(visible_after=10_000)
    with pytest.raises(NotionSyncError, match="rerun sync"):
        sync(make_experiment(tmp_path), "parent", api)
    assert api.creates == 1
    assert api.lookups == 1 + ne.RECONCILE_ATTEMPTS


def test_create_response_without_id_is_sync_error(tmp_path: Path) -> None:
    class NoId(FakeAPI):
        def call(
            self, method: str, endpoint: str, payload: dict[str, Any] | None = None
        ) -> dict[str, Any]:
            return {}

    with pytest.raises(NotionSyncError, match="page id"):
        sync(make_experiment(tmp_path), "parent", NoId())


def test_main_dry_run_prints_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv("NOTION_EXPERIMENTS_PAGE_ID", raising=False)
    assert ne.main([str(make_experiment(tmp_path)), "--dry-run"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "dry-run"


@pytest.mark.parametrize(
    ("env", "message"),
    [
        ({}, "NOTION_EXPERIMENTS_PAGE_ID"),
        ({"NOTION_EXPERIMENTS_PAGE_ID": PARENT}, "NOTION_TOKEN"),
        ({"NOTION_EXPERIMENTS_PAGE_ID": "../x", "NOTION_TOKEN": "t"}, "page ID"),
    ],
)
def test_main_reports_actionable_config_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    env: dict[str, str],
    message: str,
) -> None:
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv("NOTION_EXPERIMENTS_PAGE_ID", raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    with pytest.raises(SystemExit) as info:
        ne.main([str(make_experiment(tmp_path))])
    assert info.value.code == 2
    assert message in capsys.readouterr().err


def test_main_failure_is_isolated_from_local_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    path = make_experiment(tmp_path)
    before = (path / "manifest.json").read_bytes()
    monkeypatch.setenv("NOTION_TOKEN", "tok")
    monkeypatch.setenv("NOTION_EXPERIMENTS_PAGE_ID", PARENT)
    script_urlopen(monkeypatch, [URLError("offline")])
    assert ne.main([str(path)]) == 1
    failure = json.loads(capsys.readouterr().err)
    assert failure["sync_status"] == "failed"
    assert failure["local_artifacts"] == "untouched"
    assert (path / "manifest.json").read_bytes() == before


def test_display_path_never_shows_paths_outside_the_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    assert ne.display_path(project / "experiments" / "EXP-1") == "experiments/EXP-1"
    assert ne.display_path(tmp_path / "elsewhere" / "manifest.json") == "manifest.json"
    assert ne.display_path(None) == "<unknown>"


def test_main_missing_manifest_does_not_leak_absolute_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "EXP-9").mkdir()
    assert ne.main(["EXP-9", "--dry-run"]) == 1
    error = json.loads(capsys.readouterr().err)["error"]
    assert error == "FileNotFoundError: cannot read EXP-9/manifest.json"
    assert str(tmp_path) not in error


def test_main_publishes_with_scripted_api(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("NOTION_TOKEN", "tok")
    monkeypatch.setenv("NOTION_EXPERIMENTS_PAGE_ID", PARENT)
    script_urlopen(monkeypatch, [b'{"results": [], "has_more": false}', b'{"id": "new-page"}'])
    assert ne.main([str(make_experiment(tmp_path))]) == 0
    assert json.loads(capsys.readouterr().out)["page_id"] == "new-page"
