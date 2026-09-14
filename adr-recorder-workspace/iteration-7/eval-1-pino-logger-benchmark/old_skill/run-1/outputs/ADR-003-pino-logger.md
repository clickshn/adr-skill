# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 애플리케이션 로거를 winston에서 pino로 교체한다.
- **Scope:** order-api (로깅 레이어, src/logger.js)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston(^3.13.0)으로 로깅한다(src/logger.js, JSON 포맷 + Console transport). API 서버에 autocannon으로 부하 테스트를 해 보니, 로거를 pino로 바꿨을 때 p99 지연과 처리량이 크게 좋아졌다. 이에 따라 로거 교체를 결정했다.

### Constraints

- 유지보수가 계속되는 라이브러리여야 한다(후보였던 bunyan은 마지막 릴리스가 3년 전이라 제외).
- 기존 호출부(src/server.js의 `logger.info(...)`)는 src/logger.js가 export하는 인스턴스를 그대로 쓴다. 교체는 src/logger.js 한 곳에서 끝나야 한다.

## Decision

### Selected

- **Technology:** pino ^9.4.0 (dependencies), pino-pretty ^11.2.2 (devDependencies, 로컬 개발용 가독성 출력)
- **Architecture:** 로거 인스턴스는 계속 src/logger.js 한 곳에서 만들어 export하고, 호출부는 바꾸지 않는다.
- **Implementation:** package.json 반영 완료(winston 제거, pino·pino-pretty 추가). src/logger.js는 아직 `require('winston')` 상태라 pino로 다시 작성해야 한다.

## Rationale

1. 같은 API 서버에서 autocannon으로 측정했을 때 p99 지연이 38ms에서 21ms로 약 45% 줄었고, 처리량은 초당 8.2k에서 11.5k req로 약 40% 늘었다.
2. 다른 후보 bunyan은 마지막 릴리스가 3년 전이라 유지보수가 멈춘 것으로 보고 제외했다.

## Evidence

- **Benchmark:** autocannon, order-api 서버. winston: p99 38ms, 8.2k req/s. pino: p99 21ms, 11.5k req/s. 측정 조건(대상 엔드포인트, 동시 연결 수, 지속 시간)은 기록되지 않았다.

## Alternatives

### winston 유지 (현행)

- **Cons:** 같은 조건의 벤치마크에서 p99 38ms, 8.2k req/s로 pino보다 느렸다.
- **Rejected because:** pino로 바꿨을 때 p99가 38ms에서 21ms로, 처리량이 8.2k에서 11.5k req/s로 개선됐다.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이다.
- **Rejected because:** 유지보수가 멈춘 것으로 판단했다.
- **Recheck if:** bunyan 유지보수가 재개되는 경우

## Consequences

### Positive

- API 서버의 p99 지연이 줄고(38ms → 21ms) 처리량이 늘어난다(8.2k → 11.5k req/s).

### Negative

- 로그 출력 스키마가 바뀐다. winston JSON 포맷은 `level: "info"`, `message`를 쓰고, pino 기본 출력은 `level: 30`(숫자), `msg`, `time`, `pid`, `hostname`을 쓴다.
- src/logger.js를 pino API로 다시 작성해야 한다.

### Risks

- package.json에서 winston은 빠졌지만 src/logger.js는 아직 `require('winston')`을 호출한다. 이 상태에서 새로 설치(npm install/ci)하면 서버가 시작할 때 `Cannot find module 'winston'`으로 실패한다.
- 로그 수집·검색·알림 규칙이 `message` 필드나 문자열 level에 기대고 있다면 교체 후 깨질 수 있다.
- 메타데이터 인자 순서가 다르다(winston은 `info(msg, meta)`, pino는 `info(obj, msg)`). 현재 호출부는 문자열 한 개만 넘기므로 지금은 영향이 없지만, 앞으로 추가하는 호출에서 실수할 수 있다.
- 벤치마크 조건이 기록되지 않아 수치를 다시 재현하거나 비교하기 어렵다.

## Implementation

- [ ] src/logger.js를 pino로 다시 작성(level `info` 유지, 개발 환경에서만 pino-pretty transport 사용)
- [ ] 테스트: 서버 기동과 `/health` 응답 확인, 로그 출력 형식 확인
- [ ] 모니터링: 배포 후 p99 지연과 처리량이 벤치마크 수준인지 확인
- [ ] 문서/설정 업데이트: 로그 수집 파이프라인의 필드 매핑(`message`→`msg`, level 숫자) 점검, lockfile 갱신

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json을 되돌리고(`winston: ^3.13.0` 복원, pino·pino-pretty 제거) src/logger.js를 winston 버전으로 복원한다(`git checkout HEAD -- package.json src/logger.js`). 로거 사용처는 src/logger.js 한 곳뿐이다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개되는 경우

## References

- **Documentation:** winston 도입 커밋 e49320b (feat: order-api 초기 구성). 이 교체는 아직 커밋되지 않았다(HEAD f0828fa 기준 package.json diff).
