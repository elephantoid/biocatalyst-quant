# BACKLOG
- [x] B0-01 ADR-001~008 원본 존재/버전/승인 상태 확인 (`docs/ADR-INTEGRATION.md`; 감사 원문은 로컬 전용 `diff.md`)
- [x] B0-02 코드·테스트·데이터 lineage 상태 `implemented/partial/missing/unknown` 작성 (`docs/STATUS.md`; 감사 원문은 로컬 전용 `diff.md`)
- [ ] B0-03 1개 next-start task (`B1-01`) + 예상 리스크 + 사용자 승인 (`docs/DESIGN_DECISIONS.md` `DD-002`) — 제안 완료, 승인 대기

## Reconciliation (2026-10-20, 승인됨, 완료) — SYNC ID 는 로컬 전용 `diff.md` §3 불일치 #1~#6 에 대응 (가정; 결과는 `DD-003`~`DD-008`)
- [x] SYNC-01 ADR-008 v1.1 / Notion 파일 동기화 (diff #1) — 이미 반영됨, 해시 재검증
- [x] SYNC-02 notion_experiments 품질 게이트 (diff #2) → B6-02 로 처리, ruff/mypy/bandit/pytest 통과 (`DD-006`, `DD-007`)
- [x] SYNC-03 ADR-005 v1.0 → v1.1, 원본 보존·새 해시 등록 (diff #3, `DD-005`)
- [ ] SYNC-04 ADR-006 vs `equal_weight_return` (diff #4) — **CONFLICT 유지**, `B5-01` 에서 test-first 해결. `ARCHITECTURE_REVIEW.md` 는 SUPERSEDED 배너로 보존 (`DD-008`)
- [x] SYNC-05 시간 어휘 통일 (diff #5, `DD-004`) — 문서 완료, 코드 정렬은 `B1-01`
- [x] SYNC-06 AGENTS/CLAUDE 역할 분리 (diff #6) — 변경 없음, 정보 손실 없음 확인
- [x] ENV-01 Git/uv/.venv/.secrets.baseline/hooks 부트스트랩 (`DD-003`), `quality.sh full` exit 0
- [x] B6-02 Notion 모듈 품질 수정 (ruff PT018, mypy no-any-return)

## Core (승인 대기 — 새 기능은 승인 전 착수 금지)
- [ ] B1-01 관측·공개·사용가능 timestamp 예제 fixture — `DD-004` 어휘 기준 (승인 후)
- [ ] B2-01 event/label 시간 누수 단위테스트 (승인 후)
- [ ] B4-01 purged walk-forward OOS 평가 설계 감사 — ADR-005 v1.1; window/step/embargo OPEN (승인 후)
- [ ] B5-01 `equal_weight_return` ↔ ADR-006 CONFLICT 해결, test-first (승인 후)
- [ ] B6-01 ADR-008 artifact atomic/cache 검증 계획 (승인 후)
- [ ] B7-xx Notion outbox 기반 비차단 발행 (승인 후, 이번 범위 아님)
