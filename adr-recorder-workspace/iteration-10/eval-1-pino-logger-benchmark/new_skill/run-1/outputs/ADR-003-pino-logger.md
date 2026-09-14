# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api (로깅 — src/logger.js)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston(^3.13.0)으로 JSON 로그를 Console에 출력하고 있다(src/logger.js). autocannon 부하 테스트에서 winston 사용 시 p99 지연과 처리량이 pino 대비 불리하게 측정되어 로거 교체를 결정했다.

### Constraints

- 후보 로거는 현재 유지보수가 이루어지고 있어야 한다(마지막 릴리스가 3년 전인 bunyan은 이 이유로 제외).
- 현재 로그는 level info, JSON 형식으로 stdout(Console)에 출력된다(src/logger.js).

## Decision

### Selected

- **Technology:** pino ^9.4.0 (dependencies), pino-pretty ^11.2.2 (devDependencies, 개발용 가독성 출력)
- **Architecture:** 단일 로거 모듈(src/logger.js)이 로거 인스턴스를 export하고 애플리케이션이 이를 require하는 구조는 그대로 유지한다.
- **Implementation:** package.json 의존성은 이미 교체됨(winston 제거, pino·pino-pretty 추가). src/logger.js는 아직 `require('winston')` 상태라 pino 기반으로 재작성해야 한다.

## Rationale

1. 같은 API 서버를 autocannon으로 측정했을 때 pino가 p99 지연을 38ms → 21ms로 줄였다.
2. 처리량이 초당 8.2k → 11.5k req로 늘었다.
3. 유지보수 중인 라이브러리라는 조건을 만족한다(bunyan은 여기서 탈락).

## Evidence

- **Benchmark:** order-api에서 autocannon 측정 — winston: p99 38ms / 8.2k req/s, pino: p99 21ms / 11.5k req/s (p99 약 45% 감소, 처리량 약 40% 증가). 측정 조건(엔드포인트, 동시 연결 수, 측정 시간)은 기록되지 않았다.

## Alternatives

### winston 유지 (현행)

- **Pros:** 코드 변경이 없고 이미 운영 중인 설정이다.
- **Cons:** autocannon 측정에서 pino 대비 p99가 높고(38ms vs 21ms) 처리량이 낮다(8.2k vs 11.5k req/s).
- **Rejected because:** 측정된 지연·처리량 성능이 pino보다 떨어짐.

### bunyan

- **Rejected because:** 마지막 릴리스가 3년 전으로 유지보수가 중단된 상태.
- **Recheck if:** bunyan 유지보수가 재개되는 경우.

## Consequences

### Positive

- 측정 기준 p99 지연 감소와 처리량 증가.

### Negative

- 로거 모듈을 다시 작성해야 하고, 로그 필드 구조(예: `level`이 문자열 대신 숫자로 출력, 타임스탬프 필드명)가 winston과 달라질 수 있어 로그 수집·검색 쪽 확인이 필요하다.

### Risks

- 현재 src/logger.js가 여전히 `require('winston')`인데 package.json에서 winston이 빠져, 클린 설치(`npm ci`/`npm install`) 후 서버 기동 시 `Cannot find module 'winston'`으로 실패한다. logger.js 교체 전에는 배포하면 안 된다.
- pino는 `logger.info(obj, msg)`처럼 인자 순서가 winston의 `logger.info(msg, meta)`와 다르다. 현재 호출부는 src/server.js 한 곳(문자열 메시지만 사용)이지만, 이후 메타데이터를 넘기는 호출을 추가할 때 주의가 필요하다.
- 벤치마크 측정 조건이 기록되지 않아 재현·검증이 어렵다.

## Implementation

- [x] package.json 의존성 교체 (winston 제거, pino ^9.4.0 / pino-pretty ^11.2.2 추가)
- [ ] src/logger.js를 pino 기반으로 재작성 (level: info, JSON → stdout 유지)
- [ ] 테스트: 서버 기동 및 로그 출력 확인, autocannon 벤치마크 재측정(조건 기록)
- [ ] 모니터링: 배포 후 p99 지연·처리량이 측정치에 가깝게 나오는지 확인
- [ ] 문서/설정 업데이트: 로컬 개발용 pino-pretty 사용법(예: `node src/server.js | pino-pretty`), 로그 수집 파이프라인의 필드 매핑 점검

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json에서 pino·pino-pretty를 빼고 winston ^3.13.0을 다시 넣은 뒤 src/logger.js를 winston 버전(커밋 e49320b 기준)으로 되돌린다.
- **Migration Cost:** Low (로거 설정은 src/logger.js 한 파일, 호출부는 src/server.js 한 곳)

## Review Trigger

- bunyan 유지보수가 재개되는 경우 (bunyan 재검토)

## References

- **Documentation:** winston 최초 도입 커밋 e49320b (feat: order-api 초기 구성 (express, pg, winston))
