# ADR-003: 로깅 라이브러리를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api
- **Decision Source:** Human

---

## Context

### Problem

order-api는 초기 구성부터 winston을 로거로 사용해 왔다(f6a7269). API 서버의 응답 지연과 처리량에서 로깅 오버헤드가 무시할 수 없는 수준으로 드러나, 더 가벼운 로거로 교체할지 검토가 필요했다.

### Constraints

- 기존 로그는 JSON 포맷으로 콘솔에 출력된다(`src/logger.js`의 `winston.format.json()` + Console transport). 교체 후에도 JSON 구조화 로그를 유지해야 한다.
- 로컬 개발 시 사람이 읽을 수 있는 출력이 필요해 `pino-pretty`를 devDependency로 함께 둔다.

## Decision

### Selected

- **Technology:** pino ^9.4.0 (개발용 포매터로 pino-pretty ^11.2.2)
- **Architecture:** 애플리케이션 로깅 레이어를 pino 기반 단일 로거 모듈(`src/logger.js`)로 유지하고, 로그는 stdout으로 JSON 출력한다.
- **Implementation:** `package.json`에서 winston을 제거하고 pino를 추가했으며(작업 트리에 반영, 미커밋), devDependencies에 pino-pretty를 추가했다. `src/logger.js`는 아직 winston API를 사용 중이라 pino로 교체해야 한다.

## Rationale

1. autocannon 부하 테스트에서 p99 지연이 38ms → 21ms로 약 45% 감소했다.
2. 같은 테스트에서 처리량이 초당 8.2k → 11.5k req로 약 40% 증가했다.
3. 기존과 동일한 JSON 구조화 로그를 유지할 수 있어 로그 수집 파이프라인 변경이 필요 없다.

## Evidence

- **Benchmark:** autocannon으로 API 서버 부하 측정 — p99 지연 38ms(winston) → 21ms(pino), 처리량 8.2k req/s(winston) → 11.5k req/s(pino).

## Alternatives

### winston 유지 (현행 유지)

- **Pros:** 이미 도입되어 동작 중이라 코드 변경과 회귀 위험이 없다.
- **Cons:** autocannon 측정에서 p99 38ms, 처리량 8.2k req/s로 pino 대비 지연이 크고 처리량이 낮다.
- **Rejected because:** 동일 조건 벤치마크에서 pino가 지연·처리량 양쪽 모두 뚜렷하게 우위였다.

### bunyan

- **Pros:** JSON 구조화 로깅을 기본으로 제공하는 후보였다.
- **Cons:** 마지막 릴리스가 3년 전으로 유지보수가 사실상 중단된 상태다.
- **Rejected because:** 유지보수가 중단된 라이브러리를 신규 도입하기 어렵다고 판단했다.
- **Recheck if:** bunyan의 유지보수가 재개되면 다시 후보로 검토한다.

## Consequences

### Positive

- 로깅 오버헤드 감소로 API p99 지연과 처리량이 개선된다.
- JSON 로그 포맷이 유지되어 downstream 로그 수집·검색 설정을 바꾸지 않아도 된다.

### Negative

- winston의 transport 생태계(파일·외부 전송 등)를 쓰게 될 경우 pino transport 방식으로 다시 구성해야 한다.
- 개발 환경에서 가독성 있는 출력을 위해 pino-pretty라는 의존성이 하나 늘었다.

### Risks

- 현재 `package.json`에서는 winston이 제거됐지만 `src/logger.js`는 여전히 `require('winston')`을 사용한다. 이 상태로 배포되면 서버 기동이 실패한다. 코드 교체 전까지는 미완 상태로 취급해야 한다.
- winston과 pino는 로그 레벨 필드·기본 필드(`level`, `time`, `msg` 등) 표현이 달라, 로그 기반 알림·대시보드 쿼리가 깨질 수 있다.

## Implementation

- [ ] `src/logger.js`를 pino 기반으로 교체하고 기존 `logger.info(...)` 호출부 호환 확인
- [ ] 개발 환경에서만 pino-pretty가 붙도록 설정 분기
- [ ] jest 테스트 실행 및 `/health` 기동 확인
- [ ] 로그 필드 변경에 맞춰 로그 수집·대시보드 쿼리 점검
- [ ] autocannon 재측정으로 벤치마크 수치 재현 확인

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`의 dependencies에서 pino를 winston `^3.13.0`으로 되돌리고 pino-pretty를 제거한 뒤, `src/logger.js`를 f6a7269 시점의 winston 구성으로 복원한다. 데이터 마이그레이션이나 외부 시스템 변경이 없어 되돌림은 코드 레벨에서 끝난다.
- **Migration Cost:** Low

## Review Trigger

- bunyan의 유지보수가 재개되면 로거 선택을 다시 검토한다.

## References

- **Documentation:** f6a7269 — winston을 처음 도입한 커밋(`package.json`, `src/logger.js`). 이번 변경은 아직 커밋되지 않은 작업 트리 상태다.
