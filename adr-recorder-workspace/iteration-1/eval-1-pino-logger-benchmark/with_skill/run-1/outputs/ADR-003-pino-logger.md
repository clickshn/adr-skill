# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston 3에서 pino 9로 교체한다.
- **Scope:** order-api
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston으로 로그를 남기고 있었고, autocannon 부하 테스트에서 winston 사용 시 p99 38ms, 처리량 8.2k req/s가 나왔다. 로거 오버헤드를 줄여 지연시간과 처리량을 개선할 필요가 있었다.

### Constraints

- 기존과 같이 JSON 구조화 로그를 stdout으로 출력해야 한다 (현재 `winston.format.json()` + Console transport).
- 유지보수가 계속되고 있는 라이브러리여야 한다 (bunyan 제외 사유).

## Decision

### Selected

- **Technology:** pino ^9.4.0 (dependencies), pino-pretty ^11.2.2 (devDependencies, 로컬 개발용 가독성 출력)
- **Architecture:** 단일 로거 모듈 `src/logger.js`가 로거 인스턴스를 export하고 나머지 코드는 이를 require해서 쓰는 구조를 유지한다.
- **Implementation:** `src/logger.js`의 `winston.createLogger(...)`를 `pino({ level: 'info' })`로 교체한다. 운영 환경은 pino 기본 JSON 출력을 쓰고, pino-pretty는 개발 환경에서만 쓴다.

## Rationale

1. 같은 API 서버에서 autocannon으로 측정한 결과 p99 지연이 38ms → 21ms(44.7% 감소), 처리량이 8.2k → 11.5k req/s(40.2% 증가)로 개선됐다.
2. 다른 후보였던 bunyan은 마지막 릴리스가 3년 전이라 유지보수 리스크가 있다.
3. pino도 기본 출력이 JSON이고 `logger.info(msg)` 호출 형태가 같아서, 기존 로그 형식과 호출부를 거의 그대로 유지할 수 있다.

## Evidence

- **Benchmark:** autocannon, order-api 대상 — winston: p99 38ms / 8.2k req/s, pino: p99 21ms / 11.5k req/s. 측정 조건(동시 연결 수, 지속 시간, 엔드포인트)은 기록되지 않았다.

## Alternatives

### winston (현행 유지)

- **Pros:** 이미 `src/logger.js`에 적용돼 있어 전환 비용이 없다.
- **Cons:** 동일 벤치마크에서 p99 38ms, 8.2k req/s로 pino보다 느리다.
- **Rejected because:** pino 대비 p99 17ms 느리고 처리량이 3.3k req/s 낮다.

### bunyan

- **Pros:** pino와 비슷한 JSON 구조화 로깅 방식이다.
- **Cons:** 마지막 릴리스가 3년 전이다.
- **Rejected because:** 유지보수가 사실상 멈춰 있어 장기적으로 의존하기 어렵다.
- **Recheck if:** bunyan 유지보수가 재개되는 경우.

## Consequences

### Positive

- 로깅 오버헤드가 줄어 p99 지연과 처리량이 개선된다.
- JSON 구조화 로그 형식을 그대로 유지한다.

### Negative

- 운영 로그는 raw JSON이라 로컬에서 읽으려면 pino-pretty 파이프가 필요하다.
- winston의 format/transport 설정은 pino에서 그대로 쓸 수 없고, 파일·외부 전송이 필요해지면 pino transport로 새로 구성해야 한다.

### Risks

- 현재 `src/logger.js`가 아직 `require('winston')`인데 package.json에서 winston이 빠져, 로거 코드를 교체하기 전에는 새로 설치한 환경에서 서버가 기동 시 `MODULE_NOT_FOUND`로 실패한다.
- 메타데이터 인자 순서가 다르다(winston `info(msg, meta)` / pino `info(meta, msg)`). 앞으로 메타데이터를 넘기는 코드에서 winston 방식으로 쓰면 필드가 누락된다.
- 벤치마크 조건이 기록되지 않아 재현성과 운영 트래픽에서의 효과는 아직 확인되지 않았다.

## Implementation

- [ ] `src/logger.js`를 pino 기반으로 교체
- [ ] 테스트: 서버 기동과 JSON 로그 출력 확인
- [ ] 모니터링: 배포 후 p99와 처리량을 벤치마크 값(21ms, 11.5k req/s)과 비교
- [ ] 문서/설정 업데이트: 개발용 스크립트에 pino-pretty 파이프 추가 (예: `node src/server.js | pino-pretty`)

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json에 `winston ^3.13.0`을 복원하고 pino·pino-pretty를 제거한 뒤 `src/logger.js`를 되돌린다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개되면 bunyan을 다시 검토한다.
