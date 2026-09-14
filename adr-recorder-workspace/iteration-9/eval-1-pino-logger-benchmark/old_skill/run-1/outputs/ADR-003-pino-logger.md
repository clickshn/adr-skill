# ADR-003: 로거로 pino 사용 (winston 대체)

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api (src/logger.js 및 이를 사용하는 모듈)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston 기반 로거(src/logger.js: level `info`, JSON 포맷, Console transport)를 쓰고 있다. API 서버에 autocannon 부하를 걸어 보니 로거 구현에 따라 p99 지연과 처리량이 크게 달라져, 로거 교체 여부를 결정해야 했다.

### Constraints

- 유지보수가 계속되는 라이브러리여야 한다(마지막 릴리스가 3년 전인 bunyan은 이 기준으로 후보에서 제외).
- 로거는 src/logger.js 단일 모듈에서 생성·export되고 server.js 등은 `logger.info(...)`만 호출하므로, 교체 범위는 이 모듈과 호출부에 한정된다.

## Decision

### Selected

- **Technology:** pino ^9.4.0 (dependencies), pino-pretty ^11.2.2 (devDependencies, 로컬 개발용 가독성 출력)
- **Architecture:** 기존 구조 유지 — src/logger.js가 로거 인스턴스를 생성해 export하고, 각 모듈은 이를 require해서 사용한다.
- **Implementation:** package.json에서 winston ^3.13.0을 제거하고 pino·pino-pretty를 추가(작업 트리에 반영됨, 미커밋). src/logger.js는 아직 `require('winston')` 상태다.

## Rationale

1. 같은 API 서버 autocannon 측정에서 pino가 p99 지연을 38ms → 21ms로 약 45% 줄였다.
2. 처리량이 초당 8.2k → 11.5k req로 약 40% 늘었다.
3. 다른 후보였던 bunyan은 마지막 릴리스가 3년 전이라 유지보수 리스크가 있다.

## Evidence

- **Benchmark:** autocannon, order-api 서버 — winston: p99 38ms / 8.2k req/s, pino: p99 21ms / 11.5k req/s (동시 연결 수·지속 시간·로그 레벨 등 측정 조건은 기록되지 않음)

## Alternatives

### winston 유지 (현행)

- **Pros:** 현재 src/logger.js가 winston 기반이라 코드 변경이 필요 없다.
- **Cons:** 벤치마크에서 p99 38ms, 처리량 8.2k req/s로 pino보다 느리다.
- **Rejected because:** pino 대비 p99가 17ms 높고 처리량이 초당 3.3k req 낮다.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전으로 유지보수가 멈춘 상태다.
- **Rejected because:** 유지보수 중단에 따른 장기 리스크(보안 패치·Node 버전 호환성).
- **Recheck if:** bunyan 유지보수가 재개될 때.

## Consequences

### Positive

- API 서버 p99 지연 감소(38ms → 21ms)와 처리량 증가(8.2k → 11.5k req/s).

### Negative

- 로그 JSON 형태가 바뀐다. winston은 `level: "info"`, `message` 필드를 쓰지만 pino 기본값은 숫자 level(`30`), `msg`, `time`, `pid`, `hostname` 필드를 쓰므로 로그 수집·검색 쿼리를 맞춰야 할 수 있다.
- 로컬에서 사람이 읽기 좋은 출력을 보려면 pino-pretty를 따로 붙여야 한다.

### Risks

- package.json에서 winston이 빠졌지만 src/logger.js는 여전히 `require('winston')`을 호출한다. 클린 설치 후에는 서버 기동 시 모듈을 찾지 못해 실패하므로, 커밋 전에 logger.js 전환이 필요하다.
- pino-pretty는 devDependencies에 있으므로, 프로덕션 코드에서 pino-pretty transport를 참조하면 `--omit=dev` 설치 환경에서 기동이 실패한다.

## Implementation

- [ ] 구현 작업: src/logger.js를 pino로 전환(`require('pino')({ level: 'info' })`) — package.json 변경은 반영됨
- [ ] 테스트: 서버 기동과 로그 출력(`order-api listening on 3000`) 확인, jest 테스트 통과
- [ ] 모니터링: 배포 후 p99·처리량이 벤치마크 수준인지 확인, 로그 수집 파이프라인이 pino 필드를 제대로 파싱하는지 확인
- [ ] 문서/설정 업데이트: 로컬 개발 시 pino-pretty 사용법 안내(예: `node src/server.js | npx pino-pretty`)

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json 의존성을 winston ^3.13.0으로 되돌리고(커밋 전이면 `git checkout HEAD -- package.json`) src/logger.js를 winston 버전으로 복원한다. 로거 사용처가 `logger.info` 호출뿐이라 영향 범위가 작다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개될 때 (bunyan 대안 재검토)

## References

- **Documentation:** e49320b (order-api 초기 구성 — winston 도입 커밋)
