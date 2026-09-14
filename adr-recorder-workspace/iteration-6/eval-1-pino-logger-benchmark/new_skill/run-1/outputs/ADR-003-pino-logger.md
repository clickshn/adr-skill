# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api (src/logger.js)
- **Decision Source:** Human

---

## Context

### Problem

API 서버에서 autocannon으로 부하를 걸어 보니, 로거를 winston에서 pino로 바꿨을 때 p99 지연과 처리량이 모두 크게 좋아졌다. 로깅 라이브러리가 서버 성능에 무시할 수 없는 영향을 주고 있다.

### Constraints

- 로거 교체 범위는 단일 모듈 src/logger.js이며, 호출부는 현재 `logger.info(msg)` 한 곳(src/server.js)뿐이다.
- 기존 winston 설정(level `info`, JSON 포맷, Console 출력)과 같은 수준의 출력을 유지해야 한다.

## Decision

### Selected

- **Technology:** pino ^9.4.0 (dependencies), pino-pretty ^11.2.2 (devDependencies)
- **Architecture:** 모든 호출부가 공유하는 src/logger.js 싱글톤 로거 모듈 구조는 유지하고, 내부 구현만 pino로 교체한다.
- **Implementation:** package.json에서 winston ^3.13.0을 제거하고 pino와 pino-pretty를 추가했다(미커밋). src/logger.js는 아직 winston 기반이다.

## Rationale

1. 같은 API 서버에서 측정했을 때 pino의 p99 지연이 38ms에서 21ms로 약 45% 줄었다.
2. 처리량이 초당 8.2k에서 11.5k 요청으로 약 40% 늘었다.
3. 또 다른 후보였던 bunyan은 유지보수가 중단된 상태(마지막 릴리스가 3년 전)라 제외했다.

## Evidence

- **Benchmark:** autocannon, order-api 서버 기준. p99 지연 winston 38ms → pino 21ms (-44.7%), 처리량 8.2k → 11.5k req/s (+40.2%). 측정 조건(대상 엔드포인트, 동시 연결 수, 측정 시간)은 기록되지 않았다.

## Alternatives

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이며 유지보수가 중단된 상태다.
- **Rejected because:** 유지보수가 중단된 라이브러리를 새로 도입하는 것은 적절하지 않다.
- **Recheck if:** bunyan 유지보수가 재개될 때.

## Consequences

### Positive

- API p99 지연이 줄고 처리량이 늘었다(Evidence 참고).
- pino-pretty로 개발 환경에서는 읽기 쉬운 로그를 보고, 운영 환경에서는 JSON 출력을 유지할 수 있다.

### Negative

- winston의 format/transports 설정을 그대로 쓸 수 없어 src/logger.js를 pino API로 다시 작성해야 한다.

### Risks

- 현재 src/logger.js는 여전히 `require('winston')`을 호출하지만 package.json에는 winston이 없다. 새 package.json으로 의존성을 설치하면 서버가 시작할 때 MODULE_NOT_FOUND로 실패한다.
- 메타데이터를 넘기는 인자 순서가 다르다(winston `logger.info(msg, meta)`, pino `logger.info(obj, msg)`). 앞으로 호출부를 추가할 때 winston 방식으로 작성하면 필드가 누락될 수 있다.

## Implementation

- [ ] src/logger.js를 pino 기반으로 재작성 (level `info`, JSON stdout 출력 유지)
- [ ] 테스트: 서버 기동과 `logger.info` 출력 형식 확인
- [ ] 모니터링: 운영 배포 후 p99 지연과 처리량이 벤치마크 수준인지 확인
- [ ] 문서/설정 업데이트: 개발용 pino-pretty 사용법(예: `npm start | pino-pretty`) 안내

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json의 pino, pino-pretty를 winston ^3.13.0으로 되돌리고, src/logger.js를 winston 버전(HEAD a20723d 기준)으로 복원한다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개될 때 (bunyan 재검토)

## References

- **Documentation:** package.json 의존성 변경(미커밋, HEAD a20723d 기준 diff)
