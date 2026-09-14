# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 프로세스 메모리 딕셔너리에서 Redis로 옮긴다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

세션이 각 애플리케이션 프로세스의 메모리(`app/session.py`의 `_sessions` 딕셔너리)에만 저장되어
있어 프로세스 밖에서는 공유되지 않는다. 서버를 3대로 늘리면서, 로그인한 서버가 아닌 다른 서버로
요청이 분산되면 세션을 찾지 못해 로그인이 풀리는 문제가 발생했다.

### Constraints

- 서버 3대 구성을 유지한 채 해결해야 한다.
- 기존 세션 접근 인터페이스는 `get`/`put` 두 함수로 한정되어 있어 교체 지점이 좁다.

## Decision

### Selected

- **Technology:** Redis (`redis==5.0.8`, requirements.txt에 추가됨)
- **Architecture:** 세션을 애플리케이션 프로세스 외부의 공유 저장소에 두어, 3대의 서버가 동일한
  세션 상태를 참조하도록 한다.
- **Implementation:** `app/session.py`의 `get`/`put`을 프로세스 메모리 딕셔너리 대신 Redis
  클라이언트 호출로 교체한다.

## Rationale

1. 세션을 프로세스 밖 공유 저장소로 옮기면 어떤 서버로 요청이 가도 동일한 세션을 읽을 수 있어
   서버 증설로 발생한 로그인 풀림 문제가 해소된다.
2. 세션 접근이 `get`/`put` 두 함수로 캡슐화되어 있어 저장소 교체 범위가 작다.

## Alternatives

### 현행 유지 (프로세스 메모리 세션)

- **Pros:** 외부 의존성이 없고 추가 인프라 운영 부담이 없다.
- **Cons:** 세션이 프로세스 단위로 고립되어 다중 서버 환경에서 공유되지 않는다.
- **Rejected because:** 서버를 3대로 늘리면서 로그인이 풀리는 문제가 실제로 발생했다.

## Consequences

### Positive

- 3대 서버 어디로 요청이 분산되어도 동일한 세션을 조회할 수 있다.
- 애플리케이션 프로세스 재시작 시에도 세션이 유지된다.

### Negative

- Redis라는 외부 인프라 의존성과 운영 책임이 추가된다.
- 세션 조회가 인메모리 접근에서 네트워크 호출로 바뀐다.

### Risks

- Redis가 단일 장애점이 되어, 장애 시 전체 로그인 세션이 영향을 받는다.
- 세션 데이터의 직렬화/만료(TTL) 정책을 새로 정해야 하며, 누락 시 세션이 무한정 남거나 조기에
  만료될 수 있다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체 (직렬화·TTL 포함)
- [ ] 다중 서버 환경에서 로그인 세션이 유지되는지 테스트
- [ ] Redis 가용성·연결 오류 모니터링 추가
- [ ] Redis 접속 정보 설정(환경변수) 및 배포 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 프로세스 메모리 딕셔너리 구현(커밋 69b2c22 시점)으로 되돌리고
  requirements.txt에서 `redis==5.0.8`을 제거한다. 단, 되돌리면 로그인 풀림 문제가 재발한다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py` (현행 메모리 구현, 커밋 69b2c22), `requirements.txt`
  (`redis==5.0.8` 추가, 미커밋 변경)
