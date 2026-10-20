# PROJECT SPEC — BioCatalyst Quant

## 목적
생명공학 이벤트 연구·투자 시뮬레이션 시스템. 프로젝트의 장기 가치는 point-in-time 무결성, 통계적 검증, 현실적 backtesting 및 reproducibility. 실제 투자 수익이나 라이브 트레이딩은 범위 밖.

## 무엇을 보존할 것인가
ADR-001~008 기존 원본이 최우선. 이 패키지는 ADR의 대체 문서가 아니며 새 결정을 소급 확정하지 않는다. `docs/ADR-INTEGRATION.md`와 현 코드 매핑이 먼저 필요.

## 순서
B0 existing ADR/code/data inventory → B1 point-in-time & historical universe fixtures → B2 event feature/label contract → B3 conservative execution simulator tests → B4 rolling/expanding purged WF OOS → B5 abstention/cash portfolio policy → B6 immutable DAG/run manifest → B7 report/portfolio artifact.

## 보류
새 데이터 공급업체 도입, LLM/RAG 확장, 신규 모델 튜닝은 실제 병목과 benchmark가 확인될 때만 제안. 기존 11/8 freeze 방침은 시험 중단이라는 새 사실에 따라 재승인 필요; **상태 조사까지는 구현 재개하지 않는다**.
