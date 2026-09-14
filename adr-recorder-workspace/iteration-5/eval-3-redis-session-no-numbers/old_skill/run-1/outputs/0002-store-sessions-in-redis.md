# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 로그인 세션을 각 서버 프로세스 메모리 대신 공유 Redis에 저장한다.
- **Scope:** member-portal / 세션 저장소(app/session.py)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 딕셔너리(`_sessions: dict[str, dict]`)에 저장되어, 세션을 만든 서버 프로세스에서만 조회된다.
서버를 3대로 늘리면서 로그인한 서버가 아닌 다른 서버로 요청이 가면 세션을 찾지 못해 로그인이 풀리는 문제가 발생했다.

### Constraints

- 3대의 서버 인스턴스가 같은 세션을 조회할 수 있어야 한다.
- 기존 세션 모듈의 `get(session_id)` / `put(session_id, data)` 인터페이스를 쓰는 로그인/로그아웃 API(커밋 53eba24)가 이미 있다.
- Python(FastAPI) 스택이며, 클라이언트 라이브러리는 `redis==5.0.8`로 requirements.txt에 추가되었다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 redis-py 5.0.8)
- **Architecture:** 모든 애플리케이션 서버가 하나의 공유 Redis를 세션 저장소로 사용한다. 세션 상태를 프로세스 밖으로 빼서 앱 서버를 무상태로 만든다.
- **Implementation:** `app/session.py`의 인메모리 딕셔너리를 Redis 조회/저장으로 교체하되, `get`/`put` 함수 시그니처는 유지해 호출부 변경을 최소화한다.

## Rationale

1. 세션을 서버 외부의 공유 저장소에 두면 요청이 어느 서버로 라우팅되더라도 같은 세션을 조회할 수 있어, 다중 서버 환경의 로그인 풀림 문제가 해결된다.
2. 세션 모듈이 `get`/`put` 두 함수로 캡슐화되어 있어 저장소 교체 범위가 이 모듈로 한정된다.

## Consequences

### Positive

- 서버 대수와 무관하게 로그인 상태가 유지되어, 이후 수평 확장 시 세션 문제가 재발하지 않는다.
- 앱 프로세스 재시작·배포 시에도 세션이 사라지지 않는다(Redis가 유지되는 한).

### Negative

- 운영해야 할 인프라(Redis)가 하나 늘어난다.
- 세션 조회·저장마다 네트워크 왕복이 추가되고, 세션 데이터(dict)를 직렬화(예: JSON)해야 한다.

### Risks

- Redis 장애 시 전 서버에서 세션 조회가 실패해 로그인이 전면 불가해질 수 있다(단일 장애점).
- 전환 시점에 기존 인메모리 세션은 이관되지 않으므로 로그인 중인 사용자가 한 번 재로그인해야 한다.
- 현재 `put`에는 만료 처리가 없어, Redis로 옮기면서 TTL을 지정하지 않으면 세션 키가 무기한 누적된다.
- Redis에 세션이 저장되므로 접근 인증과 네트워크 접근 제한이 필요하다.

## Implementation

- [ ] `app/session.py`의 `_sessions` 딕셔너리를 Redis 클라이언트 기반 `get`/`put`으로 교체 (세션 TTL 지정 포함)
- [ ] 테스트: 서로 다른 인스턴스에서 같은 세션 조회, 만료, Redis 연결 실패 시 동작
- [ ] 모니터링: Redis 가용성·메모리 사용량·연결 수
- [ ] 문서/설정 업데이트: Redis 접속 정보(URL·인증)를 환경 설정으로 분리하고 배포 구성에 Redis 추가

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 인메모리 딕셔너리 구현으로 되돌리고 requirements.txt에서 `redis`를 제거한다. 단, 롤백 시 Redis에 있던 세션은 버려지고, 다중 서버 환경에서는 로그인 풀림 문제가 다시 발생한다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py`(현재 인메모리 구현), `requirements.txt`(`redis==5.0.8` 추가, 미커밋), 관련 커밋 53eba24 feat: 로그인/로그아웃 API
