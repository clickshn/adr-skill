# ADR-003: 로깅 라이브러리를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 로거를 winston에서 pino로 교체한다.
- **Scope:** order-api (로깅, `src/logger.js`)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston 기반 로거(`src/logger.js`, JSON 포맷, Console transport)를 사용해 왔다. autocannon 부하 테스트에서 winston 사용 시 p99 지연 38ms, 처리량 초당 8.2k req로, 로거 교체 시(pino)보다 성능이 낮게 측정되었다.

### Constraints

- 로거는 `src/logger.js` 단일 모듈이 인스턴스를 export하고, 호출부는 `require('./logger')`로만 사용한다(현재 호출부는 `src/server.js`의 `logger.info` 1곳).
- 선택하는 라이브러리는 유지보수가 지속되고 있어야 한다(bunyan 제외 사유).

## Decision

### Selected

- **Technology:** pino `^9.4.0` (dependencies), pino-pretty `^11.2.2` (devDependencies, 로컬 개발용 가독성 출력)
- **Architecture:** `src/logger.js`가 로거 인스턴스를 export하는 구조는 유지하고 구현체만 교체한다.
- **Implementation:** `winston.createLogger({ level: 'info', format: json, transports: [Console] })`를 `pino({ level: 'info' })`로 대체한다(pino는 기본이 JSON·stdout 출력).

## Rationale

1. 동일 API 서버 벤치마크에서 p99 지연이 38ms → 21ms(약 45% 감소), 처리량이 8.2k → 11.5k req/s(약 40% 증가)로 개선되었다.
2. 다른 후보였던 bunyan은 마지막 릴리스가 3년 전으로 유지보수가 멈춰 제외했다.
3. 로거가 `src/logger.js` 한 파일에 격리되어 있어 교체 범위가 작다.

## Evidence

- **Benchmark:** autocannon, order-api 대상. winston: p99 38ms / 8.2k req/s → pino: p99 21ms / 11.5k req/s. (연결 수·지속 시간 등 autocannon 옵션은 미기록)

## Alternatives

### winston 유지

- **Pros:** 기존 코드(`src/logger.js`) 변경 불필요.
- **Cons:** 벤치마크에서 p99 38ms, 8.2k req/s로 pino 대비 열위.
- **Rejected because:** pino 대비 지연·처리량 모두 낮게 측정됨.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전(유지보수 중단 상태).
- **Rejected because:** 유지보수가 중단된 라이브러리를 새로 도입하지 않기 위해.
- **Recheck if:** bunyan 유지보수(릴리스)가 재개되는 경우.

## Consequences

### Positive

- 요청 처리 경로의 로깅 오버헤드 감소로 p99 지연·처리량 개선.

### Negative

- pino 기본 출력은 한 줄 JSON이라 로컬에서 읽기 어려워 pino-pretty를 별도로 사용해야 한다.
- 메타데이터 전달 시 인자 순서가 winston(`info(msg, meta)`)과 pino(`info(meta, msg)`)가 달라, 이후 로그 호출 작성 시 주의가 필요하다.

### Risks

- 현재 `src/logger.js`는 여전히 `require('winston')`을 사용하지만 package.json에서 winston이 제거되어, 새로 `npm install`한 환경에서는 서버 기동 시 모듈을 찾지 못해 실패한다.
- pino는 `level`을 숫자(예: info=30)로 출력해 winston JSON의 문자열 `level`과 다르므로, 로그 수집·알림 규칙이 문자열 레벨을 가정하면 깨질 수 있다.

## Implementation

- [ ] `src/logger.js`를 pino 기반으로 교체 (winston require 제거)
- [ ] 테스트: `npm test` 및 `npm start`로 서버 기동·로그 출력 확인
- [ ] 모니터링: 배포 후 p99 지연·처리량을 벤치마크 수치(21ms, 11.5k req/s)와 비교
- [ ] 문서/설정 업데이트: 로그 수집 파이프라인의 level 필드 처리 확인, 로컬 실행 시 pino-pretty 사용법 안내

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json의 `pino`/`pino-pretty`를 `winston ^3.13.0`으로 되돌리고 `src/logger.js`를 winston 구현으로 복원한다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수(릴리스)가 재개되는 경우.

## References

- **Documentation:** winston 도입 커밋 `d8342f0` (feat: order-api 초기 구성)
