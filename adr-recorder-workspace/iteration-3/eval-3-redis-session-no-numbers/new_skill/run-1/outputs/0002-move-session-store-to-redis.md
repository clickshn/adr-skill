# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 세션 저장소를 프로세스 메모리(dict)에서 Redis로 옮겨 여러 서버가 세션을 공유하게 한다.
- **Scope:** member-portal / 세션 관리(`app/session.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장되어 각 서버 프로세스의 메모리에만 존재한다. 서버를 3대로 늘린 뒤, 로그인을 처리한 서버가 아닌 다른 서버로 요청이 가면 세션을 찾지 못해 로그인이 풀리는 문제가 생겼다.

### Constraints

- 서버 3대가 모두 같은 세션을 조회할 수 있어야 한다(수평 확장 전제).
- 세션 값은 Python `dict`이므로 외부 저장소에 넣으려면 직렬화가 필요하다.
- 스택은 FastAPI(`fastapi==0.112.2`) + uvicorn(`uvicorn==0.30.6`)이다.

## Decision

### Selected

- **Technology:** Redis, Python 클라이언트 `redis==5.0.8`(`requirements.txt`에 추가됨)
- **Architecture:** 세션을 각 서버의 프로세스 메모리 대신 서버 3대가 함께 쓰는 외부 Redis에 저장한다. 요청이 어느 서버로 가도 같은 세션을 조회한다.
- **Implementation:** `app/session.py`의 `get(session_id)` / `put(session_id, data)` 시그니처는 그대로 두고, 내부 저장소만 `_sessions` dict에서 Redis 호출로 바꾼다. 현재는 의존성만 추가됐고 코드는 아직 dict 기반이다.

## Rationale

1. 세션을 서버 밖의 공유 저장소로 옮기면 요청이 어느 서버로 라우팅돼도 세션이 유지되므로, 증설 후 생긴 로그인 풀림 문제가 해결된다.
2. 세션 접근이 `app/session.py`의 두 함수(`get`, `put`)로 캡슐화되어 있어 호출부를 건드리지 않고 저장소만 교체할 수 있다.

## Evidence

- **Production Data:** 서버 3대로 증설한 환경에서 로그인이 풀리는 현상이 관측됨(사용자 보고). 발생 빈도나 영향받은 사용자 수 같은 수치는 기록되지 않음.

## Consequences

### Positive

- 서버 대수와 상관없이 세션이 공유되어 로그인 상태가 유지된다.
- 서버 프로세스를 재시작하거나 배포해도 세션이 사라지지 않는다(Redis가 살아 있는 한).

### Negative

- Redis라는 운영 대상 인프라가 하나 늘어난다(배포, 모니터링, 접근 제어).
- 세션을 조회할 때마다 네트워크 왕복이 생겨 메모리 dict 조회보다 느리다.
- 세션 dict를 직렬화/역직렬화해야 하므로 직렬화할 수 없는 값은 세션에 넣을 수 없다.

### Risks

- Redis에 장애가 나면 서버 3대 모두 세션 조회에 실패해 전체 로그인이 불가능해진다(단일 장애점).
- Redis 영속성 설정에 따라 Redis 재시작 시 세션이 유실되어 사용자가 다시 로그인해야 할 수 있다.
- 현재 dict 구현에는 세션 만료가 없다. 그대로 옮기면 Redis에 세션이 계속 쌓이므로 TTL을 정해야 한다.

## Implementation

- [ ] 구현 작업: `app/session.py`의 `_sessions` dict를 Redis 호출로 교체(`get`/`put` 시그니처 유지, 세션 dict 직렬화, TTL 설정). Redis 접속 정보는 환경 설정으로 분리
- [ ] 테스트: 한 서버에서 만든 세션을 다른 서버에서 조회할 수 있는지, Redis 연결 실패 시 어떻게 동작하는지 검증
- [ ] 모니터링: Redis 가용성, 메모리 사용량, 연결 수
- [ ] 문서/설정 업데이트: 배포 환경에 Redis 인스턴스를 구성하고 서버 3대가 같은 Redis를 바라보도록 설정

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 dict 구현으로 되돌리고 `requirements.txt`에서 `redis==5.0.8`을 제거한다. 세션은 일시 데이터라 데이터 이관은 필요 없다. 다만 롤백 시점의 세션은 모두 무효화되어 재로그인이 필요하고, 서버 3대 구성에서는 로그인 풀림 문제가 다시 생긴다.
- **Migration Cost:** Low

## References

- **Documentation:** `requirements.txt`(`redis==5.0.8` 추가, 미커밋 변경), `app/session.py`(현재 메모리 세션 구현, 커밋 b761c51에서 도입)
