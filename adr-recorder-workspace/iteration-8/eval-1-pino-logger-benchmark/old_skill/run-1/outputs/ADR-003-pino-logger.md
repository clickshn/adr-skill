# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api (로깅 모듈 `src/logger.js`)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 초기 구성(e49320b) 때부터 winston으로 로깅했다. autocannon으로 부하를 걸었을 때 winston 쪽의 p99 지연과 처리량이 pino보다 눈에 띄게 나빴고, 그래서 로거를 바꿔 API 서버 성능을 개선하려 한다.

### Constraints

- 로거 후보는 유지보수 중인(최근 릴리스가 있는) 라이브러리여야 한다. 이 기준으로 bunyan은 제외했다.
- `package.json`은 이미 바뀌었지만(`winston` 제거, `pino ^9.4.0` 추가, devDependencies에 `pino-pretty ^11.2.2` 추가) `src/logger.js`는 아직 `require('winston')`을 호출한다. 이 상태로 새로 설치하면 서버 시작 시 모듈을 찾지 못해 실패한다.

## Decision

### Selected

- **Technology:** pino ^9.4.0 (로컬 개발용 출력 포맷터로 pino-pretty ^11.2.2를 devDependency로 둔다)
- **Architecture:** 로거 모듈을 `src/logger.js` 한 곳에 두고 나머지 코드는 이 모듈을 가져다 쓰는 구조를 유지한다.
- **Implementation:** `src/logger.js`의 `winston.createLogger(...)`를 pino 인스턴스(`level: 'info'`, JSON 출력)로 바꾼다.

## Rationale

1. 같은 API 서버를 autocannon으로 측정했을 때 pino로 바꾸면 p99 지연이 38ms에서 21ms로 줄었다.
2. 같은 측정에서 처리량은 초당 8.2k req에서 11.5k req로 늘었다.
3. 또 다른 후보인 bunyan은 마지막 릴리스가 3년 전이라 유지보수 리스크가 크다.

## Evidence

- **Benchmark:** order-api 서버를 autocannon으로 측정. p99 지연 winston 38ms → pino 21ms(약 44.7% 감소), 처리량 8.2k → 11.5k req/s(약 40.2% 증가). 측정 조건(동시 연결 수, 지속 시간, 대상 엔드포인트)은 기록되지 않았다.

## Alternatives

### winston 유지

- **Pros:** 이미 `src/logger.js`에 적용되어 있어 코드를 바꿀 필요가 없다.
- **Cons:** autocannon 측정에서 p99 38ms, 처리량 8.2k req/s로 pino보다 느렸다.
- **Rejected because:** 같은 조건에서 pino가 p99 지연과 처리량 모두 더 좋았다.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이다.
- **Rejected because:** 유지보수가 멈춘 것으로 보여서 후보에서 뺐다.
- **Recheck if:** bunyan 유지보수가 재개될 때

## Consequences

### Positive

- API 서버의 p99 지연과 처리량이 개선된다(측정 기준 p99 −17ms, 처리량 +3.3k req/s).

### Negative

- `src/logger.js`를 다시 작성해야 한다. 추가 메타데이터 전달 방식이 winston(`logger.info(msg, meta)`)과 pino(`logger.info(meta, msg)`)에서 달라서, 앞으로 로그 호출을 추가할 때 인자 순서에 주의해야 한다.

### Risks

- pino의 기본 JSON 출력은 winston과 필드 형태가 다르다(`level`이 숫자, 메시지 키가 `msg`, `time`/`pid`/`hostname` 필드 추가). 로그 수집·파싱·알림 규칙이 winston 형식에 맞춰져 있다면 깨질 수 있다.
- `src/logger.js`를 전환하기 전에 `package.json`만 배포하면 서버가 시작되지 않는다.

## Implementation

- [x] `package.json` 의존성 교체 (winston → pino, pino-pretty 추가)
- [ ] 구현 작업: `src/logger.js`를 pino로 전환
- [ ] 테스트: 서버 시작 확인과 로그 출력 형식 확인 (jest)
- [ ] 모니터링: 배포 후 p99 지연과 처리량을 벤치마크 수치와 비교
- [ ] 문서/설정 업데이트: 로그 수집 파이프라인의 파싱 규칙을 pino 형식에 맞게 수정, 로컬 개발 시 pino-pretty 사용 방법 안내

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`의 `pino`/`pino-pretty`를 `winston ^3.13.0`으로 되돌리고 `src/logger.js`를 winston 버전(e49320b 시점)으로 복원한다.
- **Migration Cost:** Low (로거 사용처는 `src/logger.js`와 `src/server.js`의 호출 1곳뿐이다)

## Review Trigger

- bunyan 유지보수가 재개될 때

## References

- **Documentation:** winston 도입 커밋 e49320b (feat: order-api 초기 구성), 의존성 변경은 `package.json`(아직 커밋 안 됨)
