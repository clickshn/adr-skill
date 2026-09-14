# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston 3에서 pino 9로 교체한다.
- **Scope:** order-api (로깅 — src/logger.js)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston(`^3.13.0`)으로 로그를 남기고 있었고, autocannon 부하 테스트에서 winston 사용 시 p99 지연 38ms, 처리량 초당 8.2k req로 측정되어 로거 교체 시 성능 개선 여지가 확인되었다.

### Constraints

- 로거는 `src/logger.js` 한 모듈에서 생성해 export하고, 나머지 코드(`src/server.js`)는 `logger.info(...)` 형태로만 사용한다.
- 유지보수가 계속되는 라이브러리여야 한다(마지막 릴리스가 오래된 후보는 제외).

## Decision

### Selected

- **Technology:** pino `^9.4.0` (런타임), pino-pretty `^11.2.2` (devDependency, 로컬 개발용 가독성 출력)
- **Architecture:** 기존과 동일하게 `src/logger.js`가 로거 인스턴스를 생성·export하는 단일 진입점 구조를 유지한다.
- **Implementation:** package.json에서 winston을 제거하고 pino·pino-pretty를 추가했다(미커밋 변경). `src/logger.js`는 아직 `require('winston')`을 사용 중이라 pino로의 전환이 남아 있다.

## Rationale

1. 자사 API 서버에 autocannon으로 측정한 결과 p99 지연이 38ms → 21ms로 줄고 처리량이 초당 8.2k → 11.5k req로 늘었다.
2. 또 다른 후보인 bunyan은 마지막 릴리스가 3년 전이라 유지보수 측면에서 제외했다.

## Evidence

- **Benchmark:** autocannon, order-api 서버 — winston: p99 38ms / 8.2k req/s, pino: p99 21ms / 11.5k req/s (p99 약 45% 감소, 처리량 약 40% 증가). 측정 조건(동시 연결 수·지속 시간·대상 엔드포인트)은 기록되지 않았다.

## Alternatives

### winston 유지 (현행)

- **Pros:** 이미 `src/logger.js`에서 사용 중이라 교체 작업이 필요 없다.
- **Cons:** 동일 벤치마크에서 p99 38ms, 처리량 8.2k req/s로 pino보다 느리다.
- **Rejected because:** 벤치마크에서 pino 대비 p99 지연과 처리량 모두 열세.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전으로 유지보수가 멈춘 상태.
- **Rejected because:** 유지보수 중단(마지막 릴리스 3년 전).
- **Recheck if:** bunyan의 유지보수(릴리스)가 재개되는 경우.

## Consequences

### Positive

- API 서버의 p99 지연 감소 및 처리량 증가(Evidence 참고).

### Negative

- 로그 출력 스키마가 달라진다: winston `format.json()`은 `{"level":"info","message":...}` 형태이지만 pino 기본 출력은 `{"level":30,"time":...,"pid":...,"hostname":...,"msg":...}` 형태(숫자 level, `msg` 키)다.

### Risks

- 현재 package.json에는 winston이 없는데 `src/logger.js`는 여전히 `require('winston')`을 호출하므로, 로거 코드 전환 전에 클린 설치(`npm install`/`npm ci`) 후 서버를 기동하면 `Cannot find module 'winston'`으로 시작에 실패한다.
- 로그 수집·검색·알림이 `level` 문자열이나 `message` 키에 의존하고 있다면 스키마 변경으로 깨질 수 있다.
- 벤치마크 조건이 기록되지 않아 운영 트래픽에서 같은 폭의 개선이 재현되는지는 확인되지 않았다.

## Implementation

- [x] package.json 의존성 교체 (winston 제거, pino·pino-pretty 추가)
- [ ] `src/logger.js`를 pino 기반으로 전환 (`require('winston')` 제거)
- [ ] 테스트: 서버 기동 및 로그 출력 확인, jest 테스트 통과
- [ ] 모니터링: 배포 후 p99 지연·처리량이 벤치마크 수준으로 개선되는지 확인
- [ ] 문서/설정 업데이트: 로그 파이프라인의 필드 매핑(level·msg) 조정, 로컬 개발 시 pino-pretty 사용 방법 안내

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json의 의존성을 winston `^3.13.0`으로 되돌리고 `src/logger.js`를 winston 구현으로 복원한다. 로거 사용처가 `src/logger.js` 단일 모듈을 통하므로 변경 범위가 작다.
- **Migration Cost:** Low

## Review Trigger

- bunyan의 유지보수(릴리스)가 재개되는 경우 bunyan을 다시 검토한다.

## References

- **Documentation:** winston 도입 커밋 `e49320b` (feat: order-api 초기 구성 (express, pg, winston)); 의존성 변경은 `package.json` 워킹 트리 diff(미커밋)
