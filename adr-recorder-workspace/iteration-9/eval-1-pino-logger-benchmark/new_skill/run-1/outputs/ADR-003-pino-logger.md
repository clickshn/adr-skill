# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 애플리케이션 로거를 winston에서 pino로 교체한다.
- **Scope:** order-api (로깅: src/logger.js)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston(level info, JSON 포맷, Console transport)으로 로그를 남기고 있다(src/logger.js). API 서버에서 로거별 성능을 비교해 보니 winston 사용 시 지연 시간과 처리량이 pino보다 불리했다.

### Constraints

- 후보 로거는 현재 유지보수가 이어지고 있어야 한다(마지막 릴리스가 3년 전인 bunyan은 이 이유로 제외).

## Decision

### Selected

- **Technology:** pino ^9.4.0 (dependencies), pino-pretty ^11.2.2 (devDependencies)
- **Implementation:** package.json에서 winston ^3.13.0을 제거하고 pino를 추가했다. src/logger.js는 아직 `require('winston')`을 쓰고 있어 pino로 옮기는 작업이 남아 있다.

## Rationale

1. autocannon 측정에서 pino가 winston보다 p99 지연 시간은 짧고(38ms → 21ms) 처리량은 높았다(8.2k → 11.5k req/s).
2. 다른 후보였던 bunyan은 마지막 릴리스가 3년 전이라 유지보수가 멈춘 상태로 보고 제외했다.

## Evidence

- **Benchmark:** API 서버 대상 autocannon 측정 결과, p99 지연 시간은 winston 38ms에서 pino 21ms로, 처리량은 초당 8.2k req에서 11.5k req로 바뀌었다.

## Alternatives

### winston 유지 (현행)

- **Pros:** 코드 변경 없이 그대로 쓸 수 있다(현재 src/logger.js 구성).
- **Cons:** autocannon 측정에서 p99 38ms, 8.2k req/s로 pino(21ms, 11.5k req/s)보다 불리했다.
- **Rejected because:** 같은 조건에서 pino가 지연 시간과 처리량 모두 앞섰다.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이다.
- **Rejected because:** 유지보수가 멈춘 상태여서 제외했다.
- **Recheck if:** bunyan 유지보수가 재개되면 다시 검토한다.

## Consequences

### Positive

- 측정 기준 p99 지연 시간 약 45% 감소(38ms → 21ms), 처리량 약 40% 증가(8.2k → 11.5k req/s).

### Negative

- winston과 pino는 로깅 API 형태가 달라(예: winston `logger.info(message, meta)` / pino `logger.info(obj, msg)`) src/logger.js와 호출부를 옮겨야 한다. 현재 호출부는 src/server.js의 `logger.info` 1곳이다.

### Risks

- package.json에서 winston이 빠졌는데 src/logger.js는 아직 winston을 require한다. 이 상태로 새로 설치(npm install/ci)하면 서버 시작 시 `Cannot find module 'winston'` 오류가 난다. 로거 코드를 옮기기 전에는 배포하면 안 된다.

## Implementation

- [x] package.json 의존성 교체 (winston 제거, pino·pino-pretty 추가)
- [ ] src/logger.js를 pino 기반으로 재작성 (level info, JSON stdout 출력 유지)
- [ ] 테스트 (jest) 및 서버 기동 확인
- [ ] 모니터링: 교체 후 p99 지연 시간·처리량 확인
- [ ] 문서/설정 업데이트: 개발 환경에서 pino-pretty 사용 방법 정리

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json을 HEAD 버전(winston ^3.13.0)으로 되돌리고 pino·pino-pretty를 제거한다. src/logger.js를 pino로 옮긴 뒤라면 해당 변경도 되돌린다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개되면 bunyan을 다시 검토한다.

## References

- **Documentation:** winston 도입 커밋 e49320b (feat: order-api 초기 구성)
