# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston 3에서 pino 9로 교체한다.
- **Scope:** order-api
- **Decision Source:** Human

---

## Context

### Problem

order-api는 초기 구성(5dc32fc)부터 winston으로 로깅해 왔다. API 서버를 autocannon으로 부하 테스트해 보니 winston이 지연 시간과 처리량을 떨어뜨리고 있었다.

### Constraints

- 로거는 `src/logger.js` 모듈 하나로 노출되고 호출부(`src/server.js`)는 `logger.info(...)` 형태로 쓴다. 교체 후에도 이 모듈 인터페이스를 유지해야 한다.
- 계속 유지보수되는 라이브러리여야 한다(bunyan을 뺀 이유).

## Decision

### Selected

- **Technology:** pino ^9.4.0 (런타임), pino-pretty ^11.2.2 (devDependency, 로컬 개발 시 사람이 읽기 좋은 출력용)
- **Architecture:** `src/logger.js`가 pino 인스턴스를 export하는 단일 로거 모듈 구조는 그대로 둔다.
- **Implementation:** package.json에서 winston을 빼고 pino와 pino-pretty를 추가했다(작업 트리에 반영됨, 아직 커밋 안 됨).

## Rationale

1. 우리 API 서버 벤치마크에서 pino가 winston보다 p99 지연이 약 45% 낮고 처리량은 약 40% 높았다.
2. 다른 후보인 bunyan은 마지막 릴리스가 3년 전이라 유지보수 위험이 있다.

## Evidence

- **Benchmark:** autocannon으로 order-api 측정. p99 지연 winston 38ms → pino 21ms, 처리량 8.2k → 11.5k req/s. 측정 조건(동시 연결 수, 측정 시간, 로그 레벨)은 따로 기록되지 않았다.

## Alternatives

### winston 유지 (현행)

- **Pros:** 코드 변경이 없다.
- **Cons:** 같은 벤치마크에서 p99 38ms, 처리량 8.2k req/s로 pino보다 뒤졌다.
- **Rejected because:** 벤치마크에서 지연 시간과 처리량이 모두 pino보다 나빴다.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이다.
- **Rejected because:** 유지보수가 멈춘 것으로 보여 장기 의존성으로 쓰기 위험하다.
- **Recheck if:** bunyan 유지보수가 재개되어 새 릴리스가 나올 때.

## Consequences

### Positive

- 요청 처리 경로의 로깅 부담이 줄어 p99 지연과 처리량이 좋아진다(벤치마크 기준 38→21ms, 8.2k→11.5k req/s).

### Negative

- 로그 JSON 형태가 바뀐다. winston은 `{"level":"info","message":...}`, pino는 `{"level":30,"time":...,"msg":...}` 형태여서 이 필드에 기대는 로그 수집/검색 쿼리와 알림은 고쳐야 한다.

### Risks

- 현재 `src/logger.js`는 아직 `require('winston')`을 쓰는데 package.json에서는 winston이 빠졌다. 새로 `npm install`한 환경에서는 서버가 `Cannot find module 'winston'`으로 뜨지 않는다.
- 벤치마크 조건이 기록되지 않아 운영 트래픽에서 같은 개선 폭이 나올지는 확인되지 않았다.

## Implementation

- [ ] 구현 작업: `src/logger.js`를 pino로 바꾼다(`pino({ level: 'info' })`). 개발 환경에서만 pino-pretty transport를 쓴다.
- [ ] 테스트: `npm test`(jest)를 돌리고 서버 기동과 `logger.info` 출력을 확인한다.
- [ ] 모니터링: 배포 후 운영 p99 지연과 처리량이 벤치마크 수준으로 나오는지 확인한다.
- [ ] 문서/설정 업데이트: 로그 수집 파이프라인의 필드 매핑(`message`→`msg`, 문자열 level→숫자 level)을 수정한다.

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json의 `pino`/`pino-pretty`를 `winston ^3.13.0`으로 되돌리고 `src/logger.js`를 winston 버전으로 복원한다(git revert). 로거를 쓰는 곳이 `src/logger.js`와 `src/server.js` 한 곳뿐이다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개되어 새 릴리스가 나오면 다시 검토한다.
