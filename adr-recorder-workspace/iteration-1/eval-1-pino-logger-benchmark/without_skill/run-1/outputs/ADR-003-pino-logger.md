# ADR-003: 로깅 라이브러리를 winston에서 pino로 교체

- **Status:** Accepted
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston 3에서 pino 9로 교체한다. 로컬 개발용 출력 포매터로 pino-pretty를 devDependency로 둔다.
- **Scope:** order-api
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston(`^3.13.0`)으로 JSON 로그를 콘솔에 출력하고 있었다. 로깅 오버헤드가 API 응답 지연과 처리량에 주는 영향을 줄이기 위해 로거 교체를 검토했다.

### Measurement

API 서버에서 autocannon으로 부하를 걸어 로거만 바꿔 비교했다.

| 지표 | winston | pino | 변화 |
|------|---------|------|------|
| p99 latency | 38 ms | 21 ms | 약 45% 감소 |
| Throughput | 8.2k req/s | 11.5k req/s | 약 40% 증가 |

> 측정 조건(동시 연결 수, 지속 시간, 대상 엔드포인트, 로그 레벨)은 이 문서 작성 시점에 기록되지 않았다.

## Decision

### Selected

- **Technology:** pino `^9.4.0` (dependency)
- **Dev tooling:** pino-pretty `^11.2.2` (devDependency, 로컬 가독성용)

### Alternatives Considered

| 후보 | 결과 | 사유 |
|------|------|------|
| winston (현행 유지) | 기각 | 벤치마크에서 p99·처리량 모두 pino 대비 열세 |
| bunyan | 기각 | 마지막 릴리스가 약 3년 전으로 유지보수가 사실상 중단된 상태 |

## Rationale

1. 동일 서버 벤치마크에서 p99 지연이 38 ms → 21 ms, 처리량이 8.2k → 11.5k req/s로 개선되었다.
2. pino는 현재 활발히 유지보수되고 있어 장기 사용에 따른 리스크가 bunyan보다 낮다.

## Consequences

### Positive

- 로깅으로 인한 요청 처리 오버헤드 감소 (p99 지연, 처리량 개선).
- 출력 형식이 기본 JSON이라 기존 winston `format.json()` 출력과 성격이 같다.

### Negative / Follow-up

- `src/logger.js`가 아직 `winston`을 require하고 있어, pino 기반으로 옮기기 전까지 서버가 기동되지 않는다 (package.json에서 winston이 제거됨).
- 로그 필드 구성이 달라진다 (예: pino는 `level`을 기본적으로 숫자로 출력하고 `time`, `pid`, `hostname` 필드를 추가). 로그 수집·검색·알림 규칙이 winston 필드 형식에 의존한다면 함께 점검해야 한다.
- pino-pretty는 devDependency이므로 운영 환경에서는 사용하지 않는다.

## Revisit Conditions

- bunyan의 유지보수(정기 릴리스)가 재개되면 후보로 다시 검토할 수 있다.
