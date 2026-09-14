# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 로그인 세션 저장소를 프로세스 메모리(dict)에서 Redis로 옮겨 여러 서버가 세션을 공유하게 한다.
- **Scope:** member-portal / 세션 저장소 (app/session.py)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 각 프로세스의 메모리(`app/session.py`의 모듈 전역 dict `_sessions`)에 저장된다. 서버를 3대로 늘리면 세션이 생성된 서버가 아닌 다른 서버로 요청이 가면 세션을 찾지 못해 로그인이 풀린다. 프로세스가 재시작되거나 재배포될 때도 세션이 모두 사라진다.

### Constraints

- 서버 3대가 같은 세션 데이터를 조회·기록할 수 있어야 한다.
- 기존 세션 모듈은 `get(session_id)` / `put(session_id, data)` 두 함수만 노출하므로, 호출부를 바꾸지 않고 저장소 구현만 교체할 수 있다.
- 현재 세션에는 만료(TTL) 처리가 없다. Redis로 옮기면 만료 정책을 새로 정해야 한다.

## Decision

### Selected

- **Technology:** Redis, Python 클라이언트 `redis==5.0.8` (requirements.txt에 추가됨)
- **Architecture:** 3대의 애플리케이션 서버가 공용 Redis 하나에 세션을 두고 공유한다. 애플리케이션 서버는 세션 상태를 갖지 않는다(stateless).
- **Implementation:** `app/session.py`의 `get`/`put` 인터페이스는 그대로 두고 내부의 dict를 Redis 호출로 바꾼다. 세션 데이터(dict)는 직렬화(예: JSON)해서 `session_id` 키로 저장한다.

## Rationale

1. 서버 3대 구성에서 어느 서버로 요청이 가도 같은 세션을 조회할 수 있어서, 서버 증설 때문에 로그인이 풀리는 문제가 근본적으로 사라진다.
2. 세션이 프로세스 밖에 있으므로 서버 재시작이나 재배포에도 로그인 상태가 유지된다.
3. 세션 모듈의 인터페이스가 작아(`get`/`put`) 호출부 변경 없이 저장소만 교체할 수 있다.

## Consequences

### Positive

- 서버를 수평 확장해도 로그인 상태가 유지되고, 로드밸런서에 sticky session을 둘 필요가 없다.
- 애플리케이션 서버를 무상태로 운영할 수 있어 배포와 증설이 쉬워진다.

### Negative

- 운영·모니터링해야 하는 인프라 구성요소(Redis)가 하나 늘어난다.
- 세션 조회마다 네트워크 왕복과 직렬화 비용이 생긴다(기존에는 메모리 dict 조회).
- 전환 시점에 메모리에 있던 기존 세션은 옮겨지지 않으므로 사용자가 한 번 다시 로그인해야 한다.

### Risks

- Redis가 단일 장애 지점이 된다. Redis가 멈추면 3대 서버 모두에서 로그인·인증이 실패한다.
- TTL을 설정하지 않으면 세션 키가 계속 쌓여 Redis 메모리가 늘어난다(현재 코드에 만료 로직이 없음).
- `redis==5.0.8`의 동기 클라이언트를 FastAPI 비동기 핸들러에서 쓰면 이벤트 루프가 막힐 수 있다. `redis.asyncio` 사용 여부를 정해야 한다.

## Implementation

- [ ] `app/session.py`의 dict 저장소를 Redis 클라이언트로 교체 (`get`/`put` 시그니처 유지)
- [ ] 세션 키에 TTL(만료 시간) 설정
- [ ] 여러 인스턴스에서 로그인 후 다른 인스턴스로 요청해도 세션이 유지되는지 테스트
- [ ] Redis 연결 상태, 메모리 사용량, 지연 시간 모니터링
- [ ] Redis 접속 정보(호스트/포트/비밀번호)를 환경 설정에 추가

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 프로세스 메모리 dict 구현으로 되돌리고 requirements.txt에서 `redis`를 뺀다. 이 경우 서버를 1대로 줄이거나 sticky session을 적용해야 로그인 풀림 문제가 다시 생기지 않는다.
- **Migration Cost:** Low

## References

- **Documentation:** requirements.txt (`redis==5.0.8` 추가, 아직 커밋 전), app/session.py
