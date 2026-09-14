# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 로그인 세션 저장소를 프로세스 메모리(dict)에서 Redis로 옮겨 여러 서버가 세션을 공유하게 한다.
- **Scope:** member-portal / 세션 저장소 (app/session.py)
- **Decision Source:** Human

---

## Context

### Problem

지금은 세션을 각 서버 프로세스의 메모리(`app/session.py`의 `_sessions: dict[str, dict]`)에 저장한다. 서버를 3대로 늘리면 세션이 로그인을 처리한 프로세스에만 남는다. 그래서 다음 요청이 다른 서버로 가면 세션을 찾지 못해 로그인이 풀린다.

### Constraints

- 서버 3대에서 같은 세션을 읽고 쓸 수 있어야 한다.
- 현재 세션 모듈은 `get(session_id)` / `put(session_id, data)` 두 함수로만 쓰인다. 저장소를 바꿔도 이 인터페이스는 유지할 수 있다.
- 스택은 FastAPI 0.112.2, uvicorn 0.30.6, SQLAlchemy 2.0.32(requirements.txt 기준)다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 서버 프로세스 밖에 둔 공용 Redis를 세션 저장소로 쓰고, 모든 서버 인스턴스가 이를 공유한다.
- **Implementation:** `app/session.py`의 `get`/`put`이 프로세스 메모리 dict 대신 Redis를 읽고 쓰도록 바꾼다. 의존성은 requirements.txt에 이미 추가되어 있다.

## Rationale

1. 세션이 프로세스 밖 공용 저장소에 있으므로, 요청이 3대 중 어느 서버로 가도 같은 세션을 찾는다. 이로써 로그인이 풀리는 문제가 해결된다.
2. 세션 모듈의 `get`/`put` 인터페이스는 그대로 두고 내부 구현만 바꾸면 되므로, 호출하는 로그인/로그아웃 API의 변경 범위가 작다.

## Alternatives

### 현행 유지: 프로세스 메모리 세션

- **Pros:** 외부 인프라가 필요 없고 구현이 단순하다(dict 한 개).
- **Cons:** 세션이 프로세스마다 따로 있어 서버끼리 공유되지 않는다. 프로세스를 재시작하면 세션이 사라진다.
- **Rejected because:** 서버를 3대로 늘리면 요청이 다른 서버로 갈 때 로그인이 풀린다.

## Consequences

### Positive

- 서버 대수와 관계없이 로그인 상태가 유지된다.
- 세션이 서버 프로세스 밖에 있으므로 서버를 재시작하거나 재배포해도 세션이 유지된다.

### Negative

- 운영할 인프라(Redis 서버)가 하나 늘어난다.
- 세션을 읽고 쓸 때마다 메모리 접근 대신 네트워크 요청이 발생한다.
- 지금 세션 값은 파이썬 dict이므로, Redis에 넣으려면 직렬화와 역직렬화가 필요하다.

### Risks

- Redis에 장애가 나면 3대 서버 모두 세션을 읽지 못해 로그인이 전부 영향을 받는다.
- 세션 만료(TTL)를 설정하지 않으면 Redis에 세션이 계속 쌓일 수 있다. 현재 메모리 구현에도 만료 로직은 없다.

## Implementation

- [x] requirements.txt에 `redis==5.0.8` 추가
- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체(세션 dict 직렬화 포함)
- [ ] 테스트: 서버 여러 대 환경에서 한 서버로 로그인한 뒤 다른 서버로 요청해도 세션이 유지되는지 확인
- [ ] 모니터링: Redis 가용성과 연결 오류 감시
- [ ] 문서/설정 업데이트: Redis 접속 정보를 설정으로 분리

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 프로세스 메모리 dict 구현으로 되돌리고 requirements.txt에서 `redis`를 제거한다. 이때 Redis에 있던 세션은 사라져 사용자가 다시 로그인해야 한다. 또 서버 3대 구성에서는 로그인이 풀리는 원래 문제가 다시 생긴다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py`(현행 메모리 세션 저장소), requirements.txt 변경(`redis==5.0.8` 추가, 커밋 전, 기준 커밋 919a937)
