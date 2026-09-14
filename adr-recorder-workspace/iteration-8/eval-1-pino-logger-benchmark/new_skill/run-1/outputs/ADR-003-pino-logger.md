# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api (로깅)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston(`src/logger.js`, `format.json()` + Console transport, level `info`)으로 로그를 남기고 있다. autocannon으로 API 서버를 측정한 결과 winston 사용 시 p99 지연 38ms, 처리량 초당 8.2k req였고, 로거를 pino로 바꾸면 두 지표가 모두 개선되는 것이 확인됐다.

### Constraints

- 유지보수가 계속되는 라이브러리여야 한다 (마지막 릴리스가 3년 전인 bunyan을 후보에서 뺀 기준).

## Decision

### Selected

- **Technology:** pino ^9.4.0 (dependencies), pino-pretty ^11.2.2 (devDependencies)
- **Architecture:** `src/logger.js`가 로거 인스턴스를 만들어 export하고 나머지 코드(`src/server.js`)가 이를 require하는 단일 모듈 구조를 유지한다.
- **Implementation:** package.json에서 winston을 제거하고 pino·pino-pretty를 추가했다(미커밋). `src/logger.js`는 아직 `require('winston')` 상태라 pino 전환이 남아 있다.

## Rationale

1. 같은 API 서버를 autocannon으로 측정했을 때 p99 지연이 38ms → 21ms(약 45% 감소), 처리량이 초당 8.2k → 11.5k req(약 40% 증가)로 개선됐다.
2. 다른 후보였던 bunyan은 마지막 릴리스가 3년 전이라 제외했다.
3. 로거 사용처가 `src/logger.js`(생성)와 `src/server.js`(`logger.info` 1곳)뿐이라 교체 범위가 작다.

## Evidence

- **Benchmark:** autocannon, order-api 서버 — winston: p99 38ms / 8.2k req/s, pino: p99 21ms / 11.5k req/s. 측정 조건(연결 수, 지속 시간, 대상 엔드포인트, 로그 레벨)은 기록되지 않았다.

## Alternatives

### winston 유지 (현행)

- **Pros:** 현재 코드(`src/logger.js`)가 winston 기준이라 코드 변경이 필요 없다.
- **Cons:** 벤치마크에서 pino보다 p99 지연이 17ms 높고 처리량이 초당 3.3k req 낮았다.
- **Rejected because:** 측정된 지연·처리량 차이.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이다.
- **Rejected because:** 유지보수가 멈춘 상태(마지막 릴리스 3년 전).
- **Recheck if:** bunyan 유지보수가 재개될 때.

## Consequences

### Positive

- 요청 처리 p99 지연 감소, 처리량 증가 (Evidence 참조).

### Negative

- 로그 JSON 형식이 바뀐다. winston `format.json()`은 `{"level":"info","message":...}` 형태이고, pino 기본 출력은 `{"level":30,"time":...,"pid":...,"hostname":...,"msg":...}` 형태다(level이 숫자, `message` → `msg`). 로그를 파싱하는 수집·검색·알림 설정이 있다면 함께 고쳐야 한다(저장소 안에는 해당 설정이 없음).

### Risks

- `src/logger.js`가 여전히 `require('winston')`이다. 현재 package.json으로 의존성을 새로 설치하면 winston이 없어 서버 기동 시 `Cannot find module 'winston'`으로 실패한다. package.json 변경과 logger.js 전환을 같은 커밋에 넣어야 한다.
- 벤치마크 조건이 기록되지 않아 재현·재검증이 어렵다.

## Implementation

- [x] package.json 의존성 교체 (winston 제거, pino ^9.4.0 추가, pino-pretty ^11.2.2 devDependency 추가)
- [ ] `src/logger.js`를 pino로 전환 (level `info`, stdout JSON 출력 유지)
- [ ] 테스트: `npm test`(jest), 서버 기동 및 `/health` 응답 확인
- [ ] 모니터링: 배포 후 p99 지연·처리량이 벤치마크 수준인지 확인, 로그 수집 파싱 확인
- [ ] 문서/설정 업데이트: 로컬 개발용 pino-pretty 사용 방법 정리 (현재 scripts에 연결되어 있지 않음)

## Reversibility

- **Reversible:** Yes
- **Rollback:** 변경이 아직 미커밋이므로 `git checkout HEAD -- package.json`으로 winston 의존성을 복원한다(커밋 후라면 해당 커밋을 `git revert`). logger.js를 전환했다면 함께 되돌리고, 로그 형식 변경에 맞춰 고친 수집 설정이 있으면 그것도 되돌린다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개될 때 (bunyan 재검토)

## References

- **Documentation:** e49320b (winston 도입 커밋 — `feat: order-api 초기 구성 (express, pg, winston)`)
