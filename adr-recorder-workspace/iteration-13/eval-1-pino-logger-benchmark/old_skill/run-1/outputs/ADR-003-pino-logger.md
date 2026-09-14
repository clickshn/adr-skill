# ADR-003: 로깅 라이브러리를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api
- **Decision Source:** Human

---

## Context

### Problem

order-api의 로깅 오버헤드가 API 응답 지연과 처리량에 영향을 주고 있어, 로깅 라이브러리 교체를 검토했다.

### Constraints

- 기존 로그는 JSON 포맷으로 출력 중이므로(`src/logger.js`), 교체 후에도 구조화 로그 형식을 유지해야 한다.
- 로컬 개발 환경의 가독성을 위해 별도 포매터가 필요하다(`pino-pretty`를 devDependency로 추가).

## Decision

### Selected

- **Technology:** pino ^9.4.0 (개발 편의용 pino-pretty ^11.2.2)
- **Architecture:** 애플리케이션 로깅 레이어를 pino 기반 단일 로거 모듈로 유지한다.
- **Implementation:** `package.json`에서 winston 제거 및 pino 추가 완료. `src/logger.js`의 로거 생성 코드는 아직 winston 기반이며 pino로 교체 필요.

## Rationale

1. autocannon 부하 테스트에서 p99 지연과 처리량이 모두 유의미하게 개선됐다.
2. 기존 JSON 구조화 로그 방식을 그대로 유지할 수 있어 로그 수집 파이프라인 변경이 필요 없다.

## Evidence

- **Benchmark:** autocannon으로 API 서버 부하 측정 — p99 지연 38ms → 21ms, 처리량 초당 8.2k req → 11.5k req.

## Alternatives

### winston 유지 (현행)

- **Pros:** 추가 작업 없음, 팀이 이미 사용 중.
- **Cons:** 동일 조건 벤치마크에서 p99 38ms, 처리량 8.2k req/s로 pino 대비 열세.
- **Rejected because:** 측정된 지연·처리량이 pino보다 나빴다.

### bunyan

- **Pros:** JSON 구조화 로깅을 지원하는 후보였다.
- **Cons:** 마지막 릴리스가 3년 전으로 유지보수가 사실상 중단된 상태다.
- **Rejected because:** 마지막 릴리스가 3년 전이라 후보에서 제외했다.
- **Recheck if:** bunyan 유지보수가 재개되면 다시 검토한다.

## Consequences

### Positive

- 로깅 경로의 오버헤드 감소로 p99 지연 약 45% 단축, 처리량 약 40% 증가.

### Negative

- winston의 transport 생태계(파일·외부 전송 등)를 쓰던 코드가 있다면 pino 방식으로 다시 작성해야 한다.
- 개발 환경 로그 가독성을 위해 pino-pretty라는 의존성이 하나 늘었다.

### Risks

- `src/logger.js`가 아직 winston을 require하고 있어, 코드 교체 전까지는 의존성이 제거된 상태에서 서버가 기동되지 않는다.
- 로그 필드 이름이 라이브러리별로 달라(예: level 표기) 기존 로그 기반 알림·대시보드 쿼리가 깨질 수 있다.

## Implementation

- [ ] `src/logger.js`를 pino 기반으로 교체
- [ ] 개발 환경에서 pino-pretty 적용 및 로그 출력 확인
- [ ] 기존 로그 기반 대시보드·알림 쿼리의 필드 호환성 점검
- [ ] 교체 후 autocannon 재측정으로 벤치마크 수치 재확인

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`의 의존성을 winston ^3.13.0으로 되돌리고 `src/logger.js`의 winston 기반 로거 코드를 복원한다. 복원 기준점은 커밋 a20723d(현재 HEAD)다.
- **Migration Cost:** Low

## Review Trigger

- bunyan 유지보수가 재개되면 로깅 라이브러리 선택을 다시 검토한다.

## References

- **Documentation:** `package.json` (winston → pino 변경, 미커밋 상태), `src/logger.js`
