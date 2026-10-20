# Python engineering rules
- Prefer pure functions, dataclasses and explicit domain types; isolate side effects behind adapters.
- Use modern Python 3.12 type hints; `mypy --strict` and Ruff must pass without new ignores or `type: ignore` unless specifically justified.
- Test behavior at boundaries, malformed data, missing values and timezones; avoid mocks of the function under test.
- No broad exception swallowing; log with identifiers rather than private data.
- New dependencies need version management, threat/cost discussion and ADR when material.
