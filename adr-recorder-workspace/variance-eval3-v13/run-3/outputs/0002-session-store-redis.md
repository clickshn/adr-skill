# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 프로세스 메모리(`app/session.py`의 전역 dict)에서 Redis로 옮긴다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

로그인 세션이 각 애플리케이션 프로세스의 메모리(`app/session.py`의 `_sessions` dict)에만 저장된다.
서버를 3대로 늘리면서 요청이 다른 서버로 분산되면 그 서버에는 세션이 없어 로그인이 풀리는 문제가 발생했다.

### Constraints

- 서버는 3대로 운영하며, 특정 서버에 요청을 고정하지 않는 전제다.
- 현재 세션 접근 인터페이스는 `get(session_id)` / `put(session_id, data)` 두 개로 한정돼 있다.

## Decision

### Selected

- **Technology:** Redis (redis-py 5.0.8, `requirements.txt`에 추가됨)
- **Architecture:** 3대의 애플리케이션 서버가 공유하는 외부 Redis 인스턴스에 세션을 저장한다. 세션 상태를 애플리케이션 프로세스 밖으로 빼내 서버를 무상태(stateless)로 만든다.
- **Implementation:** `app/session.py`의 `get`/`put` 시그니처를 유지한 채 내부 구현만 Redis 클라이언트 호출로 교체한다.

## Rationale

1. 세션을 모든 서버가 공유하는 외부 저장소에 두면 요청이 어느 서버로 가도 동일한 세션을 읽을 수 있어, 로그인이 풀리는 문제의 원인 자체가 사라진다.
2. 세션 접근 지점이 `app/session.py`의 `get`/`put` 두 함수뿐이라, 호출부를 바꾸지 않고 저장소만 교체할 수 있다.

## Alternatives

### 현행 유지 (프로세스 메모리 dict)

- **Pros:** 추가 인프라나 의존성이 없고, 지금 동작하는 코드 그대로다.
- **Cons:** 세션이 프로세스에 묶여 있어 서버를 늘려도 수평 확장이 되지 않는다.
- **Rejected because:** 서버를 3대로 늘리자 서버 간에 세션이 공유되지 않아 로그인이 풀리는 문제가 실제로 발생했다.

## Consequences

### Positive

- 서버 대수와 무관하게 로그인 세션이 유지된다.
- 애플리케이션 서버가 무상태가 되어 배포·재시작 시에도 세션이 날아가지 않는다.

### Negative

- Redis라는 운영 대상 인프라와 런타임 의존성이 새로 생긴다.
- 세션 조회마다 네트워크 왕복이 추가된다.

### Risks

- Redis가 단일 장애점이 되어, 장애 시 전체 로그인이 영향을 받는다.
- 세션 만료(TTL) 정책을 새로 정해야 한다. 기존 메모리 구현에는 만료 개념이 없었다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 클라이언트 기반으로 교체 (시그니처 유지)
- [ ] 세션 TTL 및 직렬화 포맷 결정
- [ ] 서버 3대 환경에서 로그인 유지 테스트
- [ ] Redis 연결 상태·지연 모니터링 추가
- [ ] Redis 접속 정보 설정/환경변수 및 배포 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 프로세스 메모리 dict 구현으로 되돌리고 `requirements.txt`에서 `redis==5.0.8`을 제거한다. 두 파일 모두 커밋 `ba84cb2`(현재 HEAD) 시점 상태로 복원하면 된다. 다만 되돌리면 서버 3대 환경의 로그인 풀림 문제가 다시 발생한다.
- **Migration Cost:** Low

## References

- **Documentation:**
  - `app/session.py` — 현행 프로세스 메모리 세션 구현
  - `requirements.txt` — `redis==5.0.8` 추가 (미커밋 변경)
