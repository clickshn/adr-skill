# ADR-003: 로깅 라이브러리를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api
- **Decision Source:** Human

---

## Context

### Problem

order-api는 초기 구성부터 winston을 로거로 사용해 왔다. API 서버의 응답 지연과 처리량에서 로깅 오버헤드가 드러나, 더 가벼운 로거로 교체할지 검토가 필요했다.

### Constraints

- 기존 로그는 JSON 포맷으로 콘솔에 출력되고 있어, 교체 후에도 동일한 구조화 로그 출력을 유지해야 한다.
- 로컬 개발 환경에서 사람이 읽을 수 있는 출력이 필요해 pino-pretty를 devDependency로 함께 도입한다.

## Decision

### Selected

- **Technology:** pino ^9.4.0 (개발 편의용으로 pino-pretty ^11.2.2)
- **Architecture:** 애플리케이션 로깅 레이어를 winston에서 pino로 교체. 구조화 JSON 로그를 stdout으로 내보내는 방식은 유지한다.
- **Implementation:** package.json 의존성은 이미 교체 완료(winston 제거, pino·pino-pretty 추가). `src/logger.js`는 아직 winston 기반이라 pino 인스턴스 생성으로 변경이 필요하다.

## Rationale

1. autocannon 부하 테스트에서 p99 지연이 38ms → 21ms로 약 45% 감소했다.
2. 같은 테스트에서 처리량이 초당 8.2k → 11.5k req로 약 40% 증가했다.
3. 두 로거 모두 구조화 JSON 로그를 표준 출력으로 내보내므로, 로그 수집 파이프라인 변경 없이 교체 가능하다.

## Evidence

- **Benchmark:** autocannon으로 order-api 부하 측정 — p99 지연 38ms(winston) → 21ms(pino), 처리량 초당 8.2k req(winston) → 11.5k req(pino).

## Alternatives

### winston 유지 (현행 유지)

- **Pros:** 이미 도입되어 동작 중이라 추가 작업이 없다.
- **Cons:** 동일 부하 조건에서 p99 지연이 더 높고 처리량이 더 낮다.
- **Rejected because:** autocannon 측정에서 pino 대비 p99 38ms vs 21ms, 처리량 8.2k vs 11.5k req/s로 뒤졌다.

### bunyan

- **Pros:** 구조화 JSON 로깅을 제공하는 후보로 검토했다.
- **Cons:** 마지막 릴리스가 3년 전으로 유지보수가 사실상 중단된 상태다.
- **Rejected because:** 마지막 릴리스가 3년 전이라 유지보수 중단으로 판단했다.
- **Recheck if:** bunyan 유지보수가 재개되면 다시 검토한다.

## Consequences

### Positive

- 로깅 오버헤드 감소로 API 응답 지연(p99)과 처리량이 개선된다.
- 의존성이 winston보다 가벼워진다.

### Negative

- `src/logger.js`를 비롯해 winston API에 의존하는 코드를 pino API로 고쳐야 한다.
- winston의 transports/format 조합에 의존하던 설정 방식을 pino의 방식으로 다시 잡아야 한다.

### Risks

- 로그 필드 이름과 구조가 달라지면(예: level 표기, 타임스탬프 필드) 기존 로그 검색·알림 쿼리가 깨질 수 있다.
- pino-pretty가 개발 의존성이므로, 운영 환경에서 실수로 참조되지 않도록 분리해야 한다.

## Implementation

- [ ] `src/logger.js`를 pino 인스턴스 생성으로 교체하고 기존 `logger.info` 호출 인터페이스 유지 확인
- [ ] 로깅 관련 테스트 및 `npm test` 통과 확인
- [ ] 교체 후 실제 트래픽에서 p99 지연·처리량이 벤치마크와 일치하는지 모니터링
- [ ] 로컬 개발용 pino-pretty 파이프 설정을 스크립트/문서에 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json에서 pino·pino-pretty를 제거하고 winston ^3.13.0을 되돌린 뒤 `src/logger.js`를 winston 구성으로 복원한다. 현재 작업 기준점은 커밋 a20723d이며, package.json 변경은 아직 커밋되지 않아 `git checkout -- package.json`으로 즉시 되돌릴 수 있다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개되면 로거 선택을 다시 검토한다.
