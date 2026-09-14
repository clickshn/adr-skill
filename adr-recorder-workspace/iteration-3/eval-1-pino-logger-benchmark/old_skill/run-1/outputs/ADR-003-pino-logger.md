# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** API 서버의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api (API 서버 로깅)
- **Decision Source:** Human

---

## Context

### Problem

API 서버의 로깅 오버헤드가 요청 지연과 처리량에 영향을 준다. autocannon 부하 테스트에서 winston을 쓸 때 p99 38ms, 초당 8.2k req가 나왔다.

### Constraints

- 로깅 라이브러리는 계속 유지보수되는 프로젝트여야 한다. 마지막 릴리스가 오래된 후보는 제외한다.

## Decision

### Selected

- **Technology:** pino ^9.4.0 (런타임), pino-pretty ^11.2.2 (devDependencies, 개발용 출력 포맷)
- **Implementation:** package.json에서 winston ^3.13.0을 제거하고 pino와 pino-pretty를 추가한다.

## Rationale

1. 같은 API 서버에서 autocannon으로 측정했을 때 pino 쪽이 p99 지연이 약 45% 줄고(38ms → 21ms) 처리량은 약 40% 늘었다(8.2k → 11.5k req/s).
2. 다른 후보였던 bunyan은 마지막 릴리스가 3년 전이라 유지보수 측면에서 제외했다.

## Evidence

- **Benchmark:** autocannon, order-api API 서버 대상. winston: p99 38ms, 8.2k req/s / pino: p99 21ms, 11.5k req/s.

## Alternatives

### winston 유지

- **Cons:** 같은 조건 벤치마크에서 pino보다 p99가 17ms 높고, 처리량은 초당 3.3k req 낮았다.
- **Rejected because:** 벤치마크에서 지연과 처리량 모두 pino보다 나빴다.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이다.
- **Rejected because:** 유지보수가 사실상 멈춘 상태라 운영 로거로 채택하기에 위험하다.
- **Recheck if:** bunyan 유지보수(릴리스)가 재개되는 경우

## Consequences

### Positive

- 로깅 오버헤드가 줄어 API 서버의 p99 지연이 낮아지고 처리량이 늘어난다(벤치마크 기준).

### Negative

- 기존 winston 기반 로거 호출부와 설정(transport, format 등)을 pino 방식으로 옮겨야 한다.
- 개발 환경에서 사람이 읽기 좋은 출력을 보려면 pino-pretty를 따로 설정해야 한다.

### Risks

- 로그 출력 포맷(필드명, 레벨 표기 등)이 바뀌어 기존 로그 수집·검색·알림 설정이 영향을 받을 수 있다.
- 벤치마크 결과는 특정 부하 조건에서 나온 값이라 실제 운영 트래픽에서는 개선 폭이 다를 수 있다.

## Implementation

- [x] package.json 의존성 교체 (winston 제거, pino/pino-pretty 추가)
- [ ] 로거 초기화 및 호출부를 winston에서 pino로 이관
- [ ] 테스트 (로거 사용 코드 및 로그 출력 확인)
- [ ] 모니터링 (배포 후 p99 지연·처리량 확인, 로그 수집 파이프라인 정상 동작 확인)
- [ ] 문서/설정 업데이트 (lockfile 갱신, 개발 환경 pino-pretty 설정)

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json에서 pino/pino-pretty를 winston으로 되돌리고 로거 초기화·호출부를 원래대로 복원한다.
- **Migration Cost:** Medium

## Review Trigger

- bunyan 유지보수(릴리스)가 재개되는 경우
