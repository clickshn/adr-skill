# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 데이터를 프로세스 메모리 대신 Redis에 저장해 여러 서버 인스턴스가 세션을 공유하게 한다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

`app/session.py`의 세션 저장소는 프로세스 메모리 안의 `dict`(`_sessions`)다(`83bb4e5`에서 도입).
서버를 3대로 늘리면서, 로그인한 사용자의 후속 요청이 세션을 만든 인스턴스가 아닌 다른
인스턴스로 라우팅되면 세션을 찾지 못해 로그인이 풀리는 문제가 발생했다.

### Constraints

- 인스턴스가 여러 대인 상태에서 동작해야 하므로 세션 저장소는 프로세스 밖에 있어야 한다.
- 기존 저장소 인터페이스는 `get(session_id)` / `put(session_id, data)` 두 함수뿐이라, 교체 범위는 이 모듈에 한정된다.
- 현재 스택은 FastAPI + uvicorn + SQLAlchemy이며, Redis는 새로 추가되는 런타임 의존성이다(운영할 Redis 인스턴스가 필요).

## Decision

### Selected

- **Technology:** redis 5.0.8 (`requirements.txt`에 추가됨)
- **Architecture:** 애플리케이션 인스턴스 외부의 공유 세션 저장소. 모든 인스턴스가 같은 Redis를 바라보므로 어느 인스턴스가 요청을 받아도 동일한 세션을 읽는다.
- **Implementation:** `app/session.py`의 `get`/`put`을 Redis 클라이언트 호출로 교체한다. 호출부 인터페이스는 유지한다.

## Rationale

1. 로그인이 풀리는 원인이 "세션이 특정 프로세스 메모리에만 존재하는 것"이므로, 세션을 프로세스 밖 공유 저장소로 옮기면 원인이 직접 해소된다.
2. 교체 지점이 `get`/`put` 두 함수로 좁아 애플리케이션 코드 변경 범위가 작다.

## Alternatives

### 현행 유지 (프로세스 메모리 세션)

- **Pros:** 외부 의존성이 없고 코드 변경이 필요 없다.
- **Cons:** 세션이 인스턴스별로 격리되어 인스턴스 간에 공유되지 않는다.
- **Rejected because:** 서버를 3대로 늘린 뒤 요청이 다른 인스턴스로 가면 세션을 찾지 못해 로그인이 풀린다.

## Consequences

### Positive

- 인스턴스 수와 무관하게 세션이 유지되어, 스케일 아웃 후에도 로그인이 풀리지 않는다.
- 인스턴스 재배포·재시작 시 기존 세션이 사라지지 않는다.

### Negative

- Redis라는 운영 대상이 하나 늘어난다(배포, 모니터링, 접속 정보 관리).
- 세션 조회가 프로세스 내 메모리 접근에서 네트워크 호출로 바뀐다.

### Risks

- Redis가 단일 장애점이 된다. Redis 장애 시 전체 인스턴스에서 로그인이 동작하지 않는다.
- 전환 시점에 메모리에 남아 있던 기존 세션은 이전되지 않아 사용자 재로그인이 발생할 수 있다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반 구현으로 교체 (세션 만료 TTL 포함)
- [ ] 다중 인스턴스 환경에서 로그인 유지 테스트 (인스턴스 A 로그인 → 인스턴스 B 요청)
- [ ] Redis 연결 상태·에러율 모니터링 추가
- [ ] Redis 접속 설정(호스트/포트/자격증명) 배포 환경에 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 프로세스 메모리 `dict` 구현으로 되돌리고 `requirements.txt`에서 `redis==5.0.8`을 제거한다. 현재 HEAD(`bd074f7`)가 이전 상태의 복원 기준점이다. 되돌리면 이 ADR이 해결하려던 다중 인스턴스 로그인 풀림 문제가 다시 나타난다.
- **Migration Cost:** Low

## References

- **Related ADR:** ADR-0001
- **Documentation:** `app/session.py`, `requirements.txt`
