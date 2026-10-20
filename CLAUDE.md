# Claude Code project instructions

Project: BioCatalyst Quant — Reproducible Research

**Read in order:** `docs/PROJECT_SPEC.md`, `docs/ACCEPTANCE.md`, `tasks/BACKLOG.md`, `docs/STATUS.md`, `docs/DESIGN_DECISIONS.md`.

Role: implementer/tester, not autonomous product owner. Prompt must map to exactly one approved backlog ID. On first launch perform read-only inventory, then stop and request scope approval.

## 공동 운영 프로토콜
1. 먼저 저장소의 코드·문서·테스트·git status를 읽어 `implemented / partial / missing / unknown`을 근거와 함께 분리.
2. 작업 전에 `docs/DESIGN_DECISIONS.md`에 문제, 후보 설계 최소 2개, 트레이드오프, 오류 가능성, 실험/검증 방법을 적는다.
3. **승인 없이 제품 범위·아키텍처·기술스택 변경 금지**. 권한이 없으면 구현 대신 제안서를 작성한다.
4. 하나의 작업만 변경. 테스트는 실제 실행한 명령과 결과를 그대로 기록. 실행하지 못했다면 `NOT RUN`.
5. 변경 코드와 중요한 의존성 호출 경로를 사용자에게 설명하게 하고, 실패 반례 1개 이상과 대안 1개 이상 제시.
6. 완료 체크는 `docs/ACCEPTANCE.md`의 증거 Gate를 통과한 경우에만. 실패 시 `blocked`.
7. 외부 게시·실거래·유료 API·파괴적 명령·git push/merge는 명시적 승인 필요. 비밀키·개인정보를 기록하거나 커밋하지 않는다.

### Claude Code output format
`INVENTORY` (file refs) → `PROPOSAL` (task ID/choices) → `APPROVAL NEEDED` → after approval `DIFF` / `TEST COMMAND+OUTPUT` / `COUNTEREXAMPLE` / `USER EXPLANATION QUESTIONS` / `STATUS UPDATE`.

Do not pretend files exist or tests pass. If tool capability is absent, state missing and propose manual check.
