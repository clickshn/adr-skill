# ADR-003: 로깅 라이브러리를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston으로 JSON 로그를 Console transport에 출력해 왔다. autocannon 부하 테스트에서 winston 구성의 응답 지연(p99)과 처리량이 병목으로 드러나, 로깅 라이브러리 교체를 검토했다.

### Constraints

- 로깅 라이브러리는 유지보수가 활성 상태여야 한다.
- 기존 스택(Express 4, Node, `src/logger.js` 단일 로거 모듈) 위에서 동작해야 한다.

## Decision

### Selected

- **Technology:** pino ^9.4.0 (개발 환경 가독성용으로 pino-pretty ^11.2.2를 devDependency로 추가)
- **Architecture:** `src/logger.js`가 로거 인스턴스를 단독 export하고 `src/server.js`가 이를 주입받는 기존 구조를 유지한 채 구현체만 교체한다.
- **Implementation:** package.json에서 winston을 제거하고 pino/pino-pretty를 추가하는 변경은 이미 적용됨(미커밋). `src/logger.js`는 아직 winston 기반이라 교체가 남아 있다.

## Rationale

1. 동일한 API 서버에 autocannon을 돌린 실측에서 p99 지연과 처리량이 모두 개선됐다.
2. 로그 포맷(JSON)과 로거 모듈 경계를 그대로 두고 구현체만 바꾸면 되므로 교체 범위가 작다.
3. 후보 중 유지보수가 활성인 라이브러리를 택했다.

## Evidence

- **Benchmark:** autocannon(order-api 대상) — p99 38ms → 21ms, 처리량 8.2k → 11.5k req/s

## Alternatives

### winston 유지 (현행)

- **Pros:** 이미 `src/logger.js`에 적용돼 있어 추가 작업이 없음.
- **Cons:** 동일 벤치마크에서 p99 38ms, 처리량 8.2k req/s로 pino 대비 열세.
- **Rejected because:** autocannon 실측에서 지연·처리량 모두 pino보다 나빴다.

### bunyan

- **Pros:** JSON 구조적 로깅을 제공하는 후보였다.
- **Cons:** 마지막 릴리스가 3년 전으로 유지보수가 사실상 중단된 상태.
- **Rejected because:** 유지보수가 중단된 것으로 판단해 후보에서 제외했다.
- **Recheck if:** bunyan 유지보수가 재개되면 다시 검토한다(사용자 명시).

## Consequences

### Positive

- 로깅 경로의 응답 지연(p99)과 처리량이 개선된다.
- 로거 모듈 인터페이스가 유지되므로 호출부(`src/server.js`) 변경이 최소화된다.

### Negative

- winston의 transport/format 생태계(파일·외부 싱크 등)에 의존하게 되면 pino 방식(transport 워커)으로 다시 설계해야 한다.
- 개발 환경에서 사람이 읽는 로그를 보려면 pino-pretty 파이프가 추가로 필요하다.

### Risks

- `src/logger.js`가 아직 winston 기반이라, package.json에서 winston이 빠진 현재 상태로 배포하면 모듈 해석이 실패한다. 코드 교체 전까지 배포 금지.
- 로그 필드명·레벨 표기가 winston과 달라 기존 로그 수집/알림 규칙이 깨질 수 있다.

## Implementation

- [ ] `src/logger.js`를 pino 기반으로 교체하고 `src/server.js` 호출부 확인
- [ ] `npm test`(jest) 통과 확인, 로그 출력 스모크 테스트
- [ ] autocannon 재측정으로 p99 21ms·11.5k req/s 재현 확인
- [ ] 로그 수집/대시보드의 필드명·레벨 매핑 갱신, 개발용 pino-pretty 실행 방법 문서화

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json의 pino/pino-pretty를 제거하고 winston ^3.13.0을 복원한 뒤 `src/logger.js`를 winston `createLogger` 구성으로 되돌린다. 현재 HEAD(6abee39)가 winston 상태의 복원 기준점이다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개되면 로깅 라이브러리 선택을 다시 검토한다.
