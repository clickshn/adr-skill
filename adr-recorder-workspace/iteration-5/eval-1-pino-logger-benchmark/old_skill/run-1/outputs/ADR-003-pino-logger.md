# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Accepted
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston 3에서 pino 9로 교체한다.
- **Scope:** order-api (src/logger.js 및 이를 사용하는 전 모듈)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston(`src/logger.js`, JSON 포맷 + Console transport)으로 로그를 남겨 왔다. API 서버에 autocannon으로 부하를 걸었을 때 로거 구현에 따라 지연·처리량 차이가 크게 나타나서, 요청 경로에 있는 로거를 더 가벼운 라이브러리로 바꿀지 결정해야 했다.

### Constraints

- 로거 생성은 `src/logger.js` 한 곳에 캡슐화되어 있고, 현재 호출부는 `src/server.js`의 `logger.info(...)` 1곳이다.
- 계속 유지보수되는 라이브러리여야 한다. 마지막 릴리스가 오래된 후보는 제외한다.

## Decision

### Selected

- **Technology:** pino ^9.4.0 (dependencies), pino-pretty ^11.2.2 (devDependencies, 개발 환경 가독성용)
- **Architecture:** 기존과 동일하게 `src/logger.js`가 로거 인스턴스를 만들어 export하는 단일 모듈 구조를 유지한다.
- **Implementation:** package.json은 교체 완료. `src/logger.js`는 아직 `require('winston')` 상태라 pino 기반으로 다시 작성해야 한다.

## Rationale

1. 동일 API 서버 autocannon 측정에서 p99 지연이 38ms에서 21ms로 약 45% 줄었다.
2. 같은 측정에서 처리량이 초당 8.2k에서 11.5k req로 약 40% 늘었다.
3. 또 다른 후보였던 bunyan은 유지보수가 멈춘 상태여서(마지막 릴리스 3년 전) 제외했다.

## Evidence

- **Benchmark:** autocannon, order-api 서버 대상. winston: p99 38ms, 8.2k req/s → pino: p99 21ms, 11.5k req/s. (연결 수, 지속 시간, 대상 엔드포인트 같은 측정 조건은 기록되지 않았다.)

## Alternatives

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이라 유지보수가 멈춘 상태다.
- **Rejected because:** 유지보수가 끊긴 라이브러리를 새로 도입하면 보안 패치나 Node 버전 호환을 기대할 수 없다.
- **Recheck if:** bunyan 유지보수(릴리스)가 재개될 때.

### winston 유지 (현상 유지)

- **Pros:** 코드 변경이 필요 없고, 기존 로그 포맷을 그대로 유지한다.
- **Cons:** 측정에서 p99 38ms, 8.2k req/s로 pino보다 느렸다.
- **Rejected because:** 벤치마크에서 pino가 p99 지연과 처리량 모두 확실히 우세했다.

## Consequences

### Positive

- 요청 처리 지연(p99)이 줄고 처리량이 늘어난다(측정 기준 p99 -45%, 처리량 +40%).
- pino-pretty로 개발 환경에서 사람이 읽기 좋은 로그를 보면서, 운영에서는 JSON 출력을 유지할 수 있다.

### Negative

- 로그 출력 스키마가 달라진다. winston JSON은 `{"level":"info","message":...}` 형태이고, pino는 `{"level":30,"time":...,"pid":...,"hostname":...,"msg":...}` 형태다. 로그 수집·검색·알림 규칙을 조정해야 할 수 있다.
- 메타데이터를 넘기는 인자 순서가 다르다(winston `info(msg, meta)`, pino `info(obj, msg)`). 앞으로 추가하는 호출부에서 주의해야 한다.

### Risks

- 현재 `src/logger.js`는 여전히 `require('winston')`을 호출하지만, package.json에서 winston이 제거됐다. 이대로 `npm install` 후 배포하면 서버가 기동 시점에 `Cannot find module 'winston'`으로 실패한다.
- 벤치마크 측정 조건이 기록되지 않아서, 나중에 재현하거나 운영 환경에서 같은 개선이 나오는지 비교하기 어렵다.

## Implementation

- [ ] 구현 작업: `src/logger.js`를 pino로 다시 작성(`level: 'info'` 유지). 기존 `logger.info('...')` 호출은 그대로 호환된다.
- [ ] 테스트: jest 실행, 서버 기동 후 로그가 정상 출력되는지 확인.
- [ ] 모니터링: 배포 후 운영 p99·처리량이 벤치마크 수준으로 개선되는지 확인. 로그 파이프라인이 pino 스키마(`level` 숫자, `msg`)를 제대로 파싱하는지 확인.
- [ ] 문서/설정 업데이트: 개발용 pino-pretty 실행 방법(예: `node src/server.js | pino-pretty`)을 scripts나 README에 추가.

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json의 `pino`/`pino-pretty`를 제거하고 `winston: ^3.13.0`을 복원한다. `src/logger.js`는 커밋 5e1c798 시점의 winston 버전으로 되돌린다. 호출부는 `src/server.js` 1곳이다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수(릴리스)가 재개될 때.
