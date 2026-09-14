# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api (로깅 — src/logger.js 및 로거 사용처)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston 기반 로거(src/logger.js)를 쓰고 있었다. API 서버를 autocannon으로 측정했을 때 winston 사용 시 p99 지연과 처리량이 pino보다 나빴다. 그래서 로깅 라이브러리를 더 빠른 쪽으로 바꾸기로 했다.

### Constraints

- 유지보수가 계속되는 라이브러리여야 한다. 마지막 릴리스가 오래된 후보는 제외한다.
- 로거는 src/logger.js 한 곳에서 만들어 export하고, 사용처(src/server.js)는 `logger.info(...)`로 호출한다.

## Decision

### Selected

- **Technology:** pino ^9.4.0 (dependencies), pino-pretty ^11.2.2 (devDependencies)
- **Architecture:** 지금처럼 src/logger.js에서 로거 인스턴스를 만들어 export하고, 구현체만 winston에서 pino로 바꾼다.
- **Implementation:** package.json 반영 완료(winston ^3.13.0 제거, pino·pino-pretty 추가). src/logger.js는 아직 `require('winston')` 상태라 전환이 남아 있다.

## Rationale

1. 같은 API 서버를 autocannon으로 측정했을 때 pino가 winston보다 p99 지연이 낮고(38ms → 21ms) 처리량이 높았다(8.2k → 11.5k req/s).
2. 다른 후보였던 bunyan은 마지막 릴리스가 3년 전이라 유지보수 조건을 만족하지 못했다.

## Evidence

- **Benchmark:** autocannon, order-api 서버 — winston: p99 38ms, 처리량 8.2k req/s / pino: p99 21ms, 처리량 11.5k req/s (p99 약 45% 감소, 처리량 약 40% 증가)

## Alternatives

### winston 유지 (현행)

- **Pros:** 기존 src/logger.js가 winston으로 작성되어 있어 전환 작업이 필요 없다.
- **Cons:** autocannon 측정에서 p99 38ms, 처리량 8.2k req/s로 pino보다 나빴다.
- **Rejected because:** 측정한 지연·처리량이 pino보다 뚜렷하게 나빴다.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이다.
- **Rejected because:** 유지보수가 멈춘 상태로 보여 후보에서 뺐다.
- **Recheck if:** bunyan 유지보수가 재개될 때

## Consequences

### Positive

- 측정 기준으로 API p99 지연이 38ms에서 21ms로 줄고, 처리량이 8.2k에서 11.5k req/s로 늘어난다.

### Negative

- src/logger.js의 로거 생성 코드를 pino API로 다시 작성해야 한다.
- 기본 출력이 JSON 한 줄 형식이라, 로컬에서 사람이 읽기 좋게 보려면 pino-pretty를 따로 거쳐야 한다.

### Risks

- 지금 package.json에는 winston이 없는데 src/logger.js는 여전히 `require('winston')`을 한다. 이 상태로 새로 설치(`npm install`/`npm ci`)하면 서버가 기동하지 못한다(`Cannot find module 'winston'`). logger.js 전환은 package.json 변경과 같은 커밋으로 묶어야 한다.
- 로그 JSON 필드가 달라진다(winston json: `level: "info"`, `message` / pino 기본: `level: 30`(숫자), `msg`, `time`, `pid`, `hostname`). 로그를 파싱하는 수집·알림 쪽 설정이 있으면 확인해야 한다.
- 메타데이터를 넘기는 인자 순서가 다르다(winston `logger.info(msg, meta)` / pino `logger.info(obj, msg)`). 현재 사용처는 문자열 한 개만 넘기는 `logger.info` 호출 1곳이다.

## Implementation

- [x] package.json 의존성 교체 (winston 제거, pino ^9.4.0 추가, pino-pretty ^11.2.2 devDependency 추가)
- [ ] 구현 작업: src/logger.js를 pino 기반으로 다시 작성 (level `info`, JSON 출력을 기존과 맞춤)
- [ ] 테스트: 새로 설치한 환경에서 서버가 기동하고 로그가 나오는지 확인
- [ ] 모니터링: 로그 수집·파싱 쪽에서 필드 변경(level 숫자화, message → msg)의 영향 확인
- [ ] 문서/설정 업데이트: 로컬 개발용 pino-pretty 사용 방법 반영 (현재 package.json scripts에는 없음)

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json을 HEAD로 되돌리면 winston ^3.13.0이 복구된다(`git checkout HEAD -- package.json`). src/logger.js를 pino로 전환했다면 그 변경도 함께 되돌린다.
- **Migration Cost:** Low — 로거 생성은 src/logger.js 한 파일에 있고, 사용처는 src/server.js의 `logger.info` 호출 1곳뿐이다.

## Review Trigger

- bunyan 유지보수가 재개되면 bunyan을 다시 검토한다.
