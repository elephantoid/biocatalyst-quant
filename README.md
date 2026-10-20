# BioCatalyst Quant — Research & Claude Code Pack v3.0

Research architecture, Python starter, local-first code quality controls. No trained alpha model, historical data licenses or live trading included.

## Quick start
```bash
uv lock
uv sync --locked
uv run pre-commit install --hook-type pre-commit --hook-type pre-push
claude
```
Before first local secrets gate, follow `docs/LOCAL_QUALITY_GATES.md` to create and audit `.secrets.baseline`. See `docs/CLAUDE_CODE_SETUP.md`. `uv.lock` must be generated after dependencies can be resolved, then committed.

## Start here
1. Read `docs/STATUS.md` (current state) and `docs/ARCHITECTURE_MASTERPLAN.md` and eight ADR files.
2. Read `docs/data-sources/QUALIFICATION_PROTOCOL.md`. None of the paid market providers has passed data qualification.
3. Implement a tiny 10-event **vertical slice**: collect → entity/time resolution → validated snapshot → feature → baseline model → conservative 5m execution → evaluate/replay.
4. Record new decisions in ADR, alternatives in `docs/RESEARCH_BACKLOG.md`.

## Scope guardrails
Maximum ten stocks, each new slot targets 10% of equity, cash allowed; use an in-sample historic universe much larger than holdings. Backtest numbers are simulations; no claims about live returns. No GitHub Actions required.

## Notion experiment journal
Completed experiments are published to Notion only by an explicit, authenticated outbound sync; local immutable registry is authoritative. See `docs/NOTION_RESEARCH_LOG.md`. Never include tokens or licensed raw datasets in journal pages.
