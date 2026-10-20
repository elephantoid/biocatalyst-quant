# Claude Code setup — local-first

Verified against official Claude Code documentation on 2026-10-16. This package **does not require GitHub Actions**.

## 1. Start

```bash
# install Claude Code using the official installation method appropriate to your OS
claude --version
uv lock
uv sync --locked
uv run pre-commit install --hook-type pre-commit --hook-type pre-push
# create and manually audit .secrets.baseline as described in docs/LOCAL_QUALITY_GATES.md
claude
```

In Claude Code, verify configuration with `/status`, inspect tools with `/permissions`, and check available project workflows via `/help`. `CLAUDE.md` is already provided; avoid `/init` blindly overwriting it.

## 2. Roles and context budget
- Root `CLAUDE.md`: short, always-on operating contract.
- `.claude/rules/*.md`: thematic engineering/temporal/security rules.
- `.claude/skills/*/SKILL.md`: on-demand repeatable workflows.
- `.claude/agents/*.md`: narrow read-only independent reviewers; delegate selectively.
- `.claude/settings.json`: conservative project permission rules; no unrestricted `Bash(*)`.
- `AGENTS.md`: interoperability for coding assistants; `CLAUDE.md` is Claude-specific.

Avoid automatic agent swarms and unconditional PostToolUse full-test hooks: they increase latency/cost and duplicate pre-commit. Use focused checks while editing, full local gate before release/push. A complex change should be planned and reviewed as a diff before commit.

## 3. Example prompts

- `/implement-feature Add immutable clinical event identity and source provenance, with tests.`
- `/review-pit Audit the historical trial record join for time leakage.`
- `/evaluate-tech Compare rules, TF-IDF classification and LLM classification for catalyst documents.`
- `/quality-gate Run the local full gate and report exact failures.`
- `Ask the research-auditor to independently review the new event-time logic.`

## 4. Operating boundaries
- Use plan mode for cross-module work, but do not overplan small fixes.
- Agents only provide suggestions; quality gates are executable and deterministic.
- No `.mcp.json` is enabled by default: register read-only/data-specific MCP services *after* defining the need and permission boundary. Do not add broker execution MCP to research environment.
- Keep per-machine user settings and credentials out of Git (`.claude/settings.local.json` is ignored).
- Offline tests are permitted, but offline passes do not mean dependency vulnerability audit complete.
- Permissions are defense-in-depth and can be influenced by user-level settings: verify effective scope with `/status` and `/permissions`.

## 5. References (official)
- https://code.claude.com/docs/en/settings
- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/best-practices
- https://code.claude.com/docs/en/permissions
