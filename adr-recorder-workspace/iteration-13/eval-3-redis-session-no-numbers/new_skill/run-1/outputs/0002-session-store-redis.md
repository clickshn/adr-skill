# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 애플리케이션 프로세스 메모리에서 Redis로 옮긴다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

세션이 `app/session.py`의 프로세스 내 딕셔너리(`_sessions`)에 저장되어 있어 각 애플리케이션 인스턴스가 자기 메모리의 세션만 알고 있다. 서버를 3대로 늘리면서 요청이 다른 인스턴스로 분산되면 해당 인스턴스에 세션이 없어 로그인이 풀리는 문제가 발생했다.

### Constraints

- 서버는 3대 구성으로 운영되며, 모든 인스턴스가 동일한 세션을 조회할 수 있어야 한다.
- 현재 세션 접근 경로는 `app/session.py`의 `get`/`put` 두 함수로 한정되어 있다.
- 의존성은 `requirements.txt`로 관리되며 `redis==5.0.8`이 이미 추가되어 있다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 인스턴스 외부의 공유 세션 저장소를 두고 3대의 애플리케이션 서버가 동일한 세션 데이터를 참조한다.
- **Implementation:** `app/session.py`의 `get`/`put` 구현을 프로세스 메모리 딕셔너리에서 Redis 클라이언트 호출로 교체한다. 호출부 인터페이스는 유지한다.

## Rationale

1. 로그인 유지가 깨지는 원인은 세션이 인스턴스별로 격리되어 있다는 점이므로, 인스턴스 바깥의 공유 저장소로 옮기면 문제가 해소된다.
2. 세션 접근이 `get`/`put` 두 함수로 캡슐화되어 있어 저장소 교체 범위가 작다.
3. Redis 클라이언트 의존성이 이미 `requirements.txt`에 추가되어 있어 결정과 코드 상태가 일치한다.

## Alternatives

### 프로세스 메모리 세션 유지 (현행)

- **Pros:** 외부 저장소 의존성이 없고, 현재 구현(`app/session.py`)이 그대로 동작한다.
- **Cons:** 세션이 인스턴스별로 격리되어 다중 서버 환경에서 공유되지 않는다.
- **Rejected because:** 서버를 3대로 늘리면서 로그인이 풀리는 문제가 실제로 발생했다.

## Consequences

### Positive

- 3대 서버 중 어느 인스턴스로 요청이 가더라도 동일한 세션을 조회할 수 있어 로그인이 유지된다.
- 인스턴스 재시작·교체 시에도 세션이 함께 사라지지 않는다.

### Negative

- Redis라는 운영 대상 인프라가 하나 늘어나며, 배포·모니터링·접속 설정이 추가로 필요하다.
- 세션 조회가 프로세스 내 접근에서 네트워크 호출로 바뀐다.

### Risks

- Redis 장애 시 전체 서버의 로그인이 동시에 영향을 받는다(단일 장애점).
- 세션 직렬화 형식과 만료(TTL) 정책을 새로 정해야 하며, 누락 시 세션이 무한히 남거나 조기에 만료될 수 있다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체하고 세션 직렬화·TTL 정책 적용
- [ ] 다중 인스턴스 환경에서 로그인 유지 확인 테스트
- [ ] Redis 가용성·연결 실패·세션 조회 실패 모니터링 추가
- [ ] Redis 접속 설정(호스트/포트/인증) 및 배포 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 69b2c22에 도입된 프로세스 메모리 딕셔너리 구현으로 되돌리고 `requirements.txt`에서 `redis==5.0.8`을 제거한다. 다만 서버 3대 구성을 유지한 채 되돌리면 로그인이 풀리는 기존 문제가 다시 발생한다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py` (현행 프로세스 메모리 구현, 69b2c22에서 도입), `requirements.txt` (`redis==5.0.8` 추가, 미커밋 변경)
