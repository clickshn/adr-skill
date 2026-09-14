# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Accepted
- **Date:** 2026-09-11
- **Decision:** order-api의 애플리케이션 로거를 winston에서 pino로 교체한다.
- **Scope:** order-api (로깅 레이어, `src/logger.js`)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston(`^3.13.0`)을 JSON 포맷 + Console transport로 사용해 왔다. API 서버에서 로거가 요청 지연(p99)과 처리량에 주는 오버헤드를 줄이려고 더 가벼운 로거로 바꾸는 방안을 검토했다.

### Constraints

- 기존과 같은 구조화(JSON) 로그를 stdout으로 출력해야 한다. 현재 winston 설정은 `level: 'info'`, `format.json()`, Console transport다.
- 유지보수가 계속되는 라이브러리여야 한다. bunyan은 이 기준으로 제외했다.

## Decision

### Selected

- **Technology:** pino `^9.4.0` (운영), pino-pretty `^11.2.2` (devDependencies, 로컬 개발용 가독성 출력)
- **Architecture:** 단일 로거 모듈(`src/logger.js`)이 인스턴스를 export하고 각 모듈이 이를 require하는 구조는 그대로 유지한다. 로그는 stdout에 JSON으로 출력한다.
- **Implementation:** `package.json` 의존성 교체는 완료했다(winston 제거, pino·pino-pretty 추가). `src/logger.js`는 아직 `require('winston')` 상태라 pino로 옮기는 작업이 남아 있다.

## Rationale

1. 자사 API 서버 부하 테스트(autocannon)에서 p99 지연이 38ms에서 21ms로 약 45% 줄었다.
2. 같은 테스트에서 처리량이 초당 8.2k req에서 11.5k req로 약 40% 늘었다.
3. 또 다른 후보 bunyan은 마지막 릴리스가 3년 전이라 유지보수 리스크가 있다. pino는 이 조건을 만족하는 후보다.

## Evidence

- **Benchmark:** 자사 API 서버 대상 autocannon 측정. winston은 p99 38ms / 8.2k req/s, pino는 p99 21ms / 11.5k req/s. 측정 조건(connections, duration, 엔드포인트)은 기록되지 않았다.

## Alternatives

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이다(사실상 유지보수 중단).
- **Rejected because:** 유지보수가 중단된 상태라 장기적으로 보안 패치·Node 버전 호환을 기대하기 어렵다.
- **Recheck if:** bunyan 유지보수가 재개되는 경우.

### winston 유지 (현상 유지)

- **Pros:** 코드 변경이 없고 이미 운영 중이다.
- **Cons:** 같은 벤치마크에서 pino보다 p99가 17ms 높고 처리량이 초당 3.3k req 낮다.
- **Rejected because:** 측정된 지연·처리량 차이가 교체 비용보다 크다고 판단했다.

## Consequences

### Positive

- API 서버의 p99 지연이 줄고 처리량이 늘어난다(벤치마크 기준).
- 운영 로그는 JSON 그대로이고, 개발 환경에서는 pino-pretty로 읽기 쉽게 볼 수 있다.

### Negative

- winston과 pino는 API 시그니처가 다르다. winston의 `logger.info(msg, meta)`는 pino에서 `logger.info(meta, msg)`이며, 호출부가 늘어날수록 이관 비용이 커진다. 현재 호출부는 `src/server.js` 1곳이다.
- pino-pretty는 devDependencies에만 있으므로 운영 환경에서 transport로 쓰면 안 된다.

### Risks

- 현재 `src/logger.js`가 여전히 winston을 require한다. 의존성을 재설치하면 서버 기동 시 `Cannot find module 'winston'` 에러가 난다.
- pino는 기본적으로 `level`을 숫자(`30` 등)로 출력한다. winston은 `"info"` 같은 문자열이다. 로그 수집·알림 파이프라인이 문자열 level에 의존한다면 `formatters.level`로 맞추거나 파이프라인을 수정해야 한다.
- 벤치마크 측정 조건이 기록되지 않아 재현·비교 검증이 어렵다.

## Implementation

- [ ] 구현 작업: `src/logger.js`를 pino 기반으로 교체(`level: 'info'` 유지, 필요 시 level 문자열 출력 설정)
- [ ] 테스트: `npm install` 후 서버 기동과 `/health` 응답을 확인하고 jest 테스트 통과를 확인
- [ ] 모니터링: 배포 후 p99 지연과 처리량이 벤치마크 수준으로 개선됐는지 확인하고, 로그 수집 파이프라인에서 로그가 정상 파싱되는지 확인
- [ ] 문서/설정 업데이트: 로컬 개발용 pino-pretty 사용법(예: `node src/server.js | pino-pretty`)을 스크립트나 문서로 정리

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json` 의존성을 winston `^3.13.0`으로 되돌리고(pino·pino-pretty 제거) `src/logger.js`를 winston 설정으로 복원한다. 로거 사용처가 `src/logger.js` 모듈 하나로 모여 있어 되돌리는 범위가 작다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개되는 경우 bunyan을 다시 검토한다.
