# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 세션 저장소를 프로세스 메모리(dict)에서 Redis로 옮겨 여러 서버가 세션을 공유하게 한다.
- **Scope:** member-portal / 세션 저장소 (app/session.py)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장되어, 각 서버 프로세스가 자기 세션만 알고 있다. 서버를 3대로 늘리면서 로그인한 서버와 다른 서버로 요청이 가면 세션을 찾지 못해 로그인이 풀리는 문제가 생긴다.

### Constraints

- 서버 3대가 같은 세션 데이터를 조회할 수 있어야 한다.
- 기존 세션 모듈의 인터페이스는 `get(session_id) -> dict | None`, `put(session_id, data)` 두 함수뿐이며, 세션 값은 `dict`이므로 Redis에 저장하려면 직렬화(예: JSON)가 필요하다.
- 현재 구현에는 세션 만료·삭제 로직이 없다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`, requirements.txt에 추가됨)
- **Architecture:** 세션 상태를 각 서버 프로세스 메모리 대신 서버 3대가 공유하는 외부 Redis에 둔다.
- **Implementation:** `app/session.py`의 `get`/`put` 시그니처는 유지하고 내부 저장소만 dict에서 Redis로 교체한다.

## Rationale

1. 세션을 공유 저장소에 두면 요청이 어느 서버로 가도 같은 세션을 조회할 수 있어, 서버 3대 환경에서 로그인이 풀리는 문제가 해소된다.

## Alternatives

### 현행 유지 (프로세스 메모리 dict 세션 저장소)

- **Pros:** 외부 의존성·인프라가 없고 구현이 가장 단순하다.
- **Cons:** 세션이 프로세스마다 따로 존재해 서버 간에 공유되지 않는다.
- **Rejected because:** 서버를 3대로 늘리자 다른 서버로 요청이 가면 로그인이 풀리는 문제가 발생했다.

## Consequences

### Positive

- 서버 대수와 무관하게 세션이 유지되어 수평 확장이 가능해진다.
- 프로세스 재시작 시에도 세션이 사라지지 않는다.

### Negative

- Redis라는 운영 대상 인프라가 하나 늘어난다.
- 세션 조회·저장마다 네트워크 왕복과 직렬화 비용이 생긴다.

### Risks

- Redis 장애 시 모든 서버에서 세션 조회가 실패해 로그인 기능 전체에 영향을 준다(단일 장애점).
- 전환 시점에 프로세스 메모리에 있던 기존 세션은 이관되지 않으므로, 로그인 중이던 사용자는 한 번 다시 로그인해야 한다.
- 현재 코드에 만료 로직이 없어, Redis로 옮길 때 만료 정책을 정하지 않으면 세션 키가 계속 쌓일 수 있다.

## Implementation

- [x] requirements.txt에 `redis==5.0.8` 추가
- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체 (세션 dict 직렬화 포함)
- [ ] 테스트: 서버 여러 대(프로세스 여러 개)에서 같은 세션이 조회되는지 확인
- [ ] 모니터링: Redis 연결 상태·오류 감시
- [ ] 문서/설정 업데이트: Redis 접속 정보 설정 추가

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 dict 구현으로 되돌리고 requirements.txt에서 `redis`를 제거한다. 단, 되돌리면 서버 여러 대 환경에서 로그인이 풀리는 문제가 다시 생긴다.
- **Migration Cost:** Low

## References

- **Related ADR:** ADR-0001 (아키텍처 결정을 ADR로 기록)
- **Documentation:** `app/session.py` (5853b90에서 도입된 프로세스 메모리 세션 저장소), `requirements.txt` 작업 트리 변경(`+redis==5.0.8`, 미커밋)
