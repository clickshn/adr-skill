# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 애플리케이션 로거를 winston에서 pino로 교체한다.
- **Scope:** order-api (로깅: src/logger.js)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston(JSON 포맷, Console transport)으로 로그를 남기고 있다. API 서버를 autocannon으로 부하 측정해 보니 winston 사용 시 p99 지연이 38ms, 처리량이 초당 8.2k req였다. 로거가 요청 경로의 지연과 처리량에 주는 부담을 줄일 필요가 있었다.

### Constraints

- 호출부는 `require('./logger')`로 가져온 인스턴스의 `logger.info(msg)` 형태에 의존한다(현재 src/server.js 1곳). 교체 후에도 같은 모듈 경로와 레벨 메서드 인터페이스를 유지해야 한다.
- 유지보수가 계속되는 라이브러리여야 한다(bunyan을 제외한 기준).

## Decision

### Selected

- **Technology:** pino ^9.4.0 (개발용 출력 포맷터 pino-pretty ^11.2.2)
- **Architecture:** src/logger.js가 pino 인스턴스를 export하고, 애플리케이션 코드는 이 모듈만 통해 로깅한다. 운영 환경은 pino 기본 JSON(stdout)을 쓰고, pino-pretty는 개발 환경에서 사람이 읽을 출력용으로만 쓴다.
- **Implementation:** package.json의 dependencies에서 winston ^3.13.0을 빼고 pino ^9.4.0을 추가했다. devDependencies에는 pino-pretty ^11.2.2를 추가했다(작업 트리 반영, 미커밋). src/logger.js는 아직 winston 기반이라 pino 기반으로 다시 작성해야 한다.

## Rationale

1. 같은 API 서버 부하 측정에서 pino가 winston보다 p99 지연이 17ms(약 45%) 낮았다.
2. 처리량이 초당 8.2k에서 11.5k req로 약 40% 늘었다.
3. 또 다른 후보였던 bunyan은 마지막 릴리스가 3년 전이라 유지보수 측면에서 뺐다.

## Evidence

- **Benchmark:** order-api 서버에 autocannon 측정. winston은 p99 38ms에 8.2k req/s, pino는 p99 21ms에 11.5k req/s였다.

## Alternatives

### winston 유지 (현행)

- **Pros:** 기존 src/logger.js를 그대로 쓸 수 있어 코드 변경과 로그 포맷 변경이 없다.
- **Cons:** 같은 측정에서 p99 38ms, 8.2k req/s로 pino보다 느리다.
- **Rejected because:** pino보다 p99 지연이 17ms 높고 처리량이 초당 3.3k req 낮다.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전으로, 유지보수가 멈춘 상태다.
- **Rejected because:** 유지보수 중단 상태의 라이브러리에 로깅을 의존하기 어렵다.
- **Recheck if:** bunyan 유지보수가 재개될 때

## Consequences

### Positive

- 요청 경로의 로깅 부담이 줄어 p99 지연과 처리량이 좋아진다(측정 기준 p99 38ms에서 21ms, 초당 8.2k에서 11.5k req).

### Negative

- 로그 출력 스키마가 바뀐다. pino 기본 출력은 `{"level":30,"time":...,"pid":...,"hostname":...,"msg":"..."}` 형태이고, winston json 포맷은 `{"level":"info","message":"..."}` 형태다. 따라서 `message` 필드나 문자열 레벨에 의존하는 로그 수집·검색 설정은 수정해야 한다.
- 메타데이터를 넘기는 인자 순서가 다르다. winston은 `logger.info(msg, meta)`, pino는 `logger.info(obj, msg)`다. 앞으로 호출부를 작성하거나 옮길 때 주의해야 한다.
- 개발 환경에서 사람이 읽을 출력을 보려면 pino-pretty 의존성과 실행 설정이 추가로 필요하다.

### Risks

- 현재 작업 트리는 package.json에서 winston이 빠졌는데 src/logger.js는 여전히 `require('winston')`을 호출한다. 이 상태로 새로 설치하면 서버 기동 시 모듈 로드에 실패한다. logger.js 교체를 package.json 변경과 같은 커밋에 넣어야 한다.
- 벤치마크 조건(동시 연결 수, 측정 시간, 대상 엔드포인트)이 기록되지 않아 재현하고 비교하기 어렵다.

## Implementation

- [x] package.json 의존성 교체(winston 제거, pino·pino-pretty 추가)
- [ ] src/logger.js를 pino 기반으로 재작성하고 기존 `level: 'info'` 설정 유지
- [ ] 테스트: 서버 기동과 로그 출력 확인, 교체된 코드 기준 autocannon 재측정
- [ ] 모니터링: 배포 후 p99 지연·처리량이 측정치 수준인지, 로그 수집 파이프라인이 새 스키마를 제대로 파싱하는지 확인
- [ ] 문서/설정 업데이트: 로그 스키마 변경 공유, 개발용 pino-pretty 실행 방법(npm script 등) 추가

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json을 winston ^3.13.0으로 되돌리고(pino·pino-pretty 제거) src/logger.js를 winston 기반으로 원복한다. 로거를 쓰는 호출부가 src/server.js 1곳뿐이라 영향 범위가 작다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개될 때(bunyan 재검토)
