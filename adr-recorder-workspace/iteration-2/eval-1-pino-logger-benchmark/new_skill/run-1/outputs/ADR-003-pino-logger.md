# ADR-003: 로깅 라이브러리를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api (로깅, `src/logger.js`)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 `src/logger.js`에서 winston 로거(`level: 'info'`, JSON 포맷, Console transport)를 하나 만들어 공유한다. autocannon 부하 테스트에서 winston 사용 시 p99 지연 38ms, 처리량 8.2k req/s였고, pino로 바꾸자 p99 21ms, 11.5k req/s가 나왔다. 로거 오버헤드가 요청 지연과 처리량에 의미 있는 영향을 주고 있었다.

### Constraints

- 유지보수가 계속되고 있는 라이브러리여야 한다(bunyan 제외 사유).
- Express 4 기반 서버(ADR-001) 위에서 동작해야 한다.

## Decision

### Selected

- **Technology:** pino `^9.4.0`(dependencies), pino-pretty `^11.2.2`(devDependencies, 로컬 개발용으로 사람이 읽기 좋은 출력)
- **Architecture:** `src/logger.js`에서 로거 인스턴스 하나를 만들어 모듈로 공유하는 기존 구조를 유지하고, 구현체만 바꾼다.
- **Implementation:** `winston.createLogger(...)`를 `pino({ level: 'info' })`로 대체한다. 현재 호출부는 `src/server.js`의 `logger.info('...')` 한 곳이고 문자열 메시지만 넘기므로 호출부는 수정할 필요가 없다.

## Rationale

1. 자사 API 서버 autocannon 측정에서 p99 지연 38ms → 21ms, 처리량 8.2k → 11.5k req/s로 개선됐다.
2. 다른 후보였던 bunyan은 마지막 릴리스가 3년 전이라 유지보수가 멈춘 상태다.
3. 로거 생성이 `src/logger.js` 한 곳에 모여 있어 교체 범위가 작다.

## Evidence

- **Benchmark:** order-api 대상 autocannon. winston: p99 38ms / 8.2k req/s → pino: p99 21ms / 11.5k req/s (p99 약 45% 감소, 처리량 약 40% 증가). 측정 조건(동시 연결 수, 지속 시간, 대상 엔드포인트, 로그 레벨)은 기록되지 않았다.

## Alternatives

### winston 유지 (현행)

- **Pros:** 이미 적용돼 있어 전환 작업이 필요 없다.
- **Cons:** 같은 벤치마크에서 p99 38ms, 8.2k req/s로 pino보다 느리다.
- **Rejected because:** pino 대비 p99 지연이 약 1.8배이고 처리량은 약 71% 수준이다.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이다.
- **Rejected because:** 유지보수가 멈춘 라이브러리라서 후보에서 뺐다.
- **Recheck if:** bunyan 유지보수가 재개될 때(새 릴리스 등).

## Consequences

### Positive

- 로깅 오버헤드가 줄어 p99 지연과 처리량이 좋아진다(측정치 기준 p99 −17ms, +3.3k req/s).

### Negative

- 로그 출력 형식이 달라진다. winston은 `{"level":"info","message":"..."}` 형태이고, pino는 `level`을 숫자(info=30)로 출력하며 메시지 키는 `msg`, 여기에 `time`, `pid`, `hostname` 필드가 붙는다. 로그 수집·검색 쿼리·대시보드가 winston 형식을 가정하고 있다면 조정해야 한다.
- 로컬 개발에서 사람이 읽을 출력을 보려면 pino-pretty로 파이프해야 한다.

### Risks

- 지금 저장소 상태에서는 서버가 기동되지 않는다. `package.json`에서 winston은 빠졌지만 `src/logger.js`가 아직 `require('winston')`을 쓰고 있어서, 새로 `npm install`한 환경에서는 `Cannot find module 'winston'`으로 실패한다. logger.js 교체는 package.json 변경과 같은 커밋에 들어가야 한다.
- 앞으로 메타데이터를 넘기는 호출을 추가할 때 인자 순서 차이(winston `logger.info(msg, meta)`, pino `logger.info(meta, msg)`)로 필드가 빠질 수 있다.
- 측정 조건이 기록되지 않아서, 운영 트래픽에서도 같은 폭으로 개선된다는 보장은 없다.

## Implementation

- [ ] `src/logger.js`를 pino로 교체(`pino({ level: 'info' })`)하고 winston require 제거
- [ ] 테스트: 서버 기동과 `logger.info` 출력 확인, `npm test`(jest) 통과
- [ ] 모니터링: 배포 후 p99와 처리량이 벤치마크 수준으로 개선되는지 확인
- [ ] 문서/설정 업데이트: 로컬 개발용 pino-pretty 실행 스크립트(예: `node src/server.js | pino-pretty`) 추가, 로그 수집 쪽 필드 매핑(`message`→`msg`, 숫자 level) 조정

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json 의존성을 winston으로 되돌리고 `src/logger.js`를 이전 버전으로 복원한다(`git revert`). 호출부는 문자열 메시지만 쓰므로 바꿀 필요가 없다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개되면(새 릴리스 등) 대안으로 다시 검토한다.
