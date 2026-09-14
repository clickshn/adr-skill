# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 애플리케이션 로거를 winston 3에서 pino 9로 교체한다.
- **Scope:** order-api (src/logger.js 및 이를 사용하는 전 모듈)
- **Decision Source:** Human

---

## Context

### Problem

API 서버에서 로거가 요청 처리 성능(지연·처리량)에 주는 오버헤드를 줄일 필요가 있었다. autocannon으로 winston과 pino를 같은 서버에서 비교한 결과 pino 쪽이 p99 지연과 처리량 모두 우세했다.

### Constraints

- 현재 로거는 `src/logger.js` 한 모듈에서 생성해 export하고(winston, level `info`, JSON 포맷, Console transport), 호출부는 `src/server.js`의 `logger.info(문자열)` 1곳뿐이다.
- 로그 출력은 stdout JSON 형태를 유지해야 한다(기존 winston 설정도 JSON + Console).
- 후보 라이브러리는 유지보수가 지속되고 있어야 한다(bunyan 제외 사유).

## Decision

### Selected

- **Technology:** pino ^9.4.0 (dependencies), pino-pretty ^11.2.2 (devDependencies, 로컬 개발용 가독성 출력)
- **Architecture:** 로거 생성은 기존처럼 `src/logger.js` 단일 진입점에서 하고, 다른 모듈은 이 모듈만 require한다.
- **Implementation:** `src/logger.js`의 `winston.createLogger(...)`를 `pino({ level: 'info' })`로 교체한다. package.json 의존성 교체는 완료됐으나(미커밋), `src/logger.js`는 아직 winston을 require하고 있다.

## Rationale

1. 자체 API 서버 벤치마크에서 p99 지연이 38ms → 21ms(약 45% 감소)로 줄었다.
2. 같은 벤치마크에서 처리량이 8.2k → 11.5k req/s(약 40% 증가)로 늘었다.
3. 또 다른 후보 bunyan은 마지막 릴리스가 3년 전이라 유지보수 리스크가 커서 제외했고, pino만 남았다.

## Evidence

- **Benchmark:** autocannon, order-api 서버 대상. winston: p99 38ms / 8.2k req/s → pino: p99 21ms / 11.5k req/s (p99 −17ms, 처리량 +3.3k req/s)

## Alternatives

### winston 유지 (현행)

- **Pros:** 코드 변경 없음. 기존 `src/logger.js` 그대로 사용 가능.
- **Cons:** 벤치마크에서 p99 38ms, 8.2k req/s로 pino보다 느리다.
- **Rejected because:** 같은 조건에서 pino 대비 p99가 17ms 높고 처리량이 3.3k req/s 낮다.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전으로 유지보수가 사실상 멈춰 있다.
- **Rejected because:** 유지보수가 중단된 라이브러리를 새로 도입하면 보안 패치·Node 버전 호환 대응을 기대하기 어렵다.
- **Recheck if:** bunyan 유지보수가 재개되어 새 릴리스가 나오는 경우.

## Consequences

### Positive

- 로깅 오버헤드가 줄어 p99 지연이 개선되고 처리량이 늘어난다(벤치마크 기준 p99 −17ms, +3.3k req/s).
- 로컬에서는 pino-pretty로 사람이 읽기 쉬운 로그를 볼 수 있다.

### Negative

- 출력 JSON 스키마가 달라진다. winston은 `{"level":"info","message":...}`, pino 기본값은 `{"level":30,"time":...,"pid":...,"hostname":...,"msg":...}` 형태여서 레벨이 숫자이고 메시지 키가 `msg`이다.
- 메타데이터를 넘기는 인자 순서가 다르다. winston은 `logger.info(msg, meta)`, pino는 `logger.info(obj, msg)`다. 현재 호출부는 문자열만 넘기므로 영향이 없지만 이후 코드는 pino 방식을 따라야 한다.

### Risks

- package.json에서 winston이 제거됐는데 `src/logger.js`는 아직 `require('winston')`을 호출한다. 이대로 `npm install` 후 기동하면 `Cannot find module 'winston'` 오류로 서버가 뜨지 않는다.
- 로그 수집·검색 쿼리나 알림이 `message` 키나 문자열 level(`"info"`)에 의존하고 있다면 교체 후 동작하지 않을 수 있다(필요 시 pino `formatters.level`로 문자열 레벨을 출력하도록 설정).
- 벤치마크 측정 조건(연결 수, 지속 시간, 실행 환경)이 기록되어 있지 않아 재현·재검증이 어렵다.

## Implementation

- [ ] `src/logger.js`를 pino로 교체 (`const pino = require('pino'); module.exports = pino({ level: 'info' });`)
- [ ] 테스트: 서버 기동과 `/health` 응답, 로그가 stdout에 JSON으로 출력되는지 확인
- [ ] 모니터링: 배포 후 운영 환경의 p99 지연과 처리량이 벤치마크 수준으로 개선됐는지 확인
- [ ] 문서/설정 업데이트: 로그 수집 파이프라인의 필드 매핑(`msg`, 숫자 level)을 점검하고, 필요하면 로컬 개발용 pino-pretty 실행 스크립트를 추가

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json의 의존성을 winston ^3.13.0으로 되돌리고(`git checkout HEAD -- package.json` 또는 해당 커밋 revert), `src/logger.js`를 winston 버전으로 복원한다. 로거 생성이 `src/logger.js` 한 곳에 모여 있어 되돌릴 범위가 작다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개되어 새 릴리스가 나오면 bunyan을 다시 비교한다.
