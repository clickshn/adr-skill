# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino 9로 교체한다.
- **Scope:** order-api
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston으로 로깅하고 있었는데, autocannon 부하 테스트에서 winston 사용 시 p99 38ms, 처리량 8.2k req/s가 나와 로거가 요청 처리 성능을 잡아먹고 있었다.

### Constraints

- 유지보수가 계속되는 라이브러리여야 한다 (마지막 릴리스가 3년 전인 bunyan을 뺀 기준).

## Decision

### Selected

- **Technology:** pino ^9.4.0 (로컬 가독성용 pino-pretty ^11.2.2, devDependency)
- **Implementation:** `src/logger.js`에서 winston 로거를 pino 인스턴스로 바꾸고, 호출부(`logger.info(...)`)의 인터페이스는 그대로 둔다.

## Rationale

1. 같은 API 서버의 autocannon 측정에서 p99 지연이 38ms → 21ms로 약 45% 줄었다.
2. 처리량이 8.2k → 11.5k req/s로 약 40% 늘었다.
3. 다른 후보 bunyan은 마지막 릴리스가 3년 전이라 유지보수 리스크가 있다.

## Evidence

- **Benchmark:** autocannon, order-api 대상 — winston: p99 38ms / 8.2k req/s, pino: p99 21ms / 11.5k req/s

## Alternatives

### winston 유지

- **Cons:** p99 38ms, 처리량 8.2k req/s로 pino보다 느리다.
- **Rejected because:** 같은 조건에서 pino가 p99 17ms 더 짧고 처리량이 초당 3.3k req 더 높다.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이다.
- **Rejected because:** 유지보수가 멈춘 상태여서 장기 의존성으로 쓰기 어렵다.
- **Recheck if:** bunyan 유지보수가 다시 시작될 때 (새 릴리스가 나올 때).

## Consequences

### Positive

- 요청 지연(p99)과 처리량이 좋아진다.
- 유지보수가 계속되는 로거를 쓰게 된다.

### Negative

- winston의 `format`/`transports` 설정을 pino 방식(옵션, transport, pino-pretty)으로 다시 작성해야 한다.

### Risks

- 로그 출력 형식(level 표기, 필드명 등)이 winston과 달라져 로그 수집이나 검색 쿼리에 영향을 줄 수 있다.
- 벤치마크 수치는 1회 측정 결과이므로, 운영 환경에서 같은 개선이 나오는지는 아직 확인되지 않았다.

## Implementation

- [ ] `src/logger.js`를 pino로 교체 — 지금도 `require('winston')`를 쓰고 있어서, winston이 빠진 package.json으로 설치하면 서버 기동 시 모듈 로드에 실패한다.
- [ ] 테스트: `logger.info` 호출부 동작 확인, autocannon 재측정으로 p99·처리량 재현 확인
- [ ] 모니터링: 배포 후 p99 지연과 처리량이 벤치마크 수준인지 확인
- [ ] 문서/설정 업데이트: 개발 환경에서 pino-pretty 출력 설정

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json의 의존성과 `src/logger.js`를 winston 버전으로 되돌린다 (로거 생성이 `src/logger.js` 한 곳에 모여 있다).
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 다시 시작되면(새 릴리스가 나오면) 재검토한다.
