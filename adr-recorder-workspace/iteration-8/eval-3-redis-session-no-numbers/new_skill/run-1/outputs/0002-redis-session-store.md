# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 로그인 세션을 각 서버 프로세스 메모리 대신 서버들이 공유하는 Redis에 저장한다.
- **Scope:** member-portal / 세션 저장소 (app/session.py)
- **Decision Source:** Human

---

## Context

### Problem

서버를 3대로 늘리면서 로그인이 풀리는 문제가 생겼다. 현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장되어 프로세스마다 따로 존재한다. 그래서 로그인한 서버와 다른 서버로 요청이 가면 세션을 찾지 못한다.

### Constraints

- 서버 3대가 같은 세션 데이터를 조회할 수 있어야 한다.
- 기존 세션 인터페이스는 `get(session_id)` / `put(session_id, data)` 두 함수이고, 세션 값은 `dict`이다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 세션 저장 위치를 각 프로세스 메모리에서 서버 3대가 공유하는 외부 Redis로 옮긴다.
- **Implementation:** `requirements.txt`에 `redis==5.0.8`를 추가했다(아직 커밋하지 않음). `app/session.py`의 `get`/`put`은 아직 dict 기반이라 Redis 기반으로 바꿔야 한다.

## Rationale

1. 세션을 서버 밖 공유 저장소에 두면 요청이 3대 중 어느 서버로 가도 같은 세션을 조회할 수 있어, 서버 증설 후 로그인이 풀리는 문제가 해소된다.

## Alternatives

### 프로세스 메모리 세션 저장소 유지 (현행)

- **Pros:** 외부 의존성이나 추가 인프라가 필요 없다. `get`/`put` 두 함수로 된 단순한 구조다.
- **Cons:** 세션이 프로세스마다 따로 존재해 서버끼리 공유되지 않는다. 프로세스를 재시작하면 세션이 사라진다.
- **Rejected because:** 서버를 3대로 늘리자 다른 서버로 요청이 가면 로그인이 풀린다.

## Consequences

### Positive

- 서버 3대가 세션을 공유해 요청이 어느 서버로 가도 로그인 상태가 유지된다.
- 세션이 애플리케이션 프로세스 밖에 있으므로 앱 서버를 재시작하거나 배포해도 세션이 유지된다.

### Negative

- 운영할 외부 인프라(Redis 서버)가 추가된다.
- 세션을 조회할 때마다 네트워크 왕복이 생긴다.
- 세션 값(`dict`)을 저장하고 읽을 때 직렬화와 역직렬화가 필요하다.

### Risks

- Redis가 장애 나면 모든 서버에서 세션 조회가 실패해 로그인 기능 전체가 영향을 받는다.
- 만료(TTL) 정책을 정하지 않으면 세션 키가 계속 쌓인다. 현재 dict 구현에도 만료 로직은 없다.

## Implementation

- [x] `requirements.txt`에 `redis==5.0.8` 추가 (미커밋)
- [ ] 구현 작업: `app/session.py`의 `get`/`put`을 Redis 클라이언트 기반으로 교체 (직렬화 포함)
- [ ] 테스트: 서로 다른 서버(프로세스)에서 같은 세션 ID로 조회되는지 확인
- [ ] 모니터링: Redis 연결 오류와 응답 지연
- [ ] 문서/설정 업데이트: 각 서버의 Redis 접속 정보 설정

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 dict 기반 구현으로 되돌리고 `requirements.txt`에서 `redis`를 제거한다. 이때 Redis에 있던 세션은 버려져 사용자가 한 번 다시 로그인해야 한다. 또 서버가 여러 대인 상태에서 되돌리면 로그인이 풀리는 문제가 다시 생긴다.
- **Migration Cost:** Low

## References

- **Documentation:** 대상 코드 `app/session.py` (커밋 5853b90에서 도입), 의존성 변경은 `requirements.txt` 작업 트리 diff(미커밋)
