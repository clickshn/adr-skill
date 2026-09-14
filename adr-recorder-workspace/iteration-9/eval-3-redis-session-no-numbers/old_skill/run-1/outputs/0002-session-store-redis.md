# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 세션 저장소를 프로세스 메모리(dict)에서 Redis로 옮겨 여러 서버가 세션을 공유하게 한다.
- **Scope:** member-portal / 세션 저장소 (app/session.py)
- **Decision Source:** Human

---

## Context

### Problem

세션이 `app/session.py`의 프로세스 메모리 dict(`_sessions`)에 저장된다. 서버를 3대로 늘리면 로그인을 처리한 서버가 아닌 다른 서버로 요청이 가는 순간 세션을 찾지 못해 로그인이 풀린다.

### Constraints

- 서버 3대 중 어느 서버가 요청을 받아도 같은 세션을 조회할 수 있어야 한다.
- 현재 세션 모듈은 `get(session_id)` / `put(session_id, data)` 두 함수로만 노출된다(만료 처리 없음).

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 각 서버 프로세스의 로컬 메모리 대신, 모든 서버가 공유하는 외부 Redis에 세션을 저장한다.
- **Implementation:** `app/session.py`의 `_sessions` dict를 Redis 호출로 교체하고, 기존 `get`/`put` 인터페이스는 유지한다. `requirements.txt`에 `redis==5.0.8`이 추가되어 있다(미커밋). `app/session.py`는 아직 dict 기반이다.

## Rationale

1. 세션을 프로세스 밖의 공유 저장소에 두면 3대 중 어느 서버가 요청을 받아도 같은 세션을 조회할 수 있어, 서버 증설로 생긴 로그인 풀림 문제가 해결된다.
2. 세션 접근이 `get`/`put` 두 함수로 모여 있어 저장소 교체 범위가 이 모듈 하나로 한정된다.

## Consequences

### Positive

- 서버 간 세션이 공유되어 어느 서버로 요청이 가도 로그인이 유지된다.
- 애플리케이션 프로세스가 재시작돼도 세션이 사라지지 않는다.

### Negative

- 운영해야 할 인프라 컴포넌트(Redis)가 하나 늘어난다.
- 세션 조회마다 네트워크 왕복이 생기고, 세션 데이터(dict)를 직렬화해야 한다.

### Risks

- Redis 장애 시 전체 서버에서 로그인·세션 조회가 불가능해진다(단일 장애 지점).
- 현재 코드에는 세션 만료가 없어, TTL을 두지 않으면 Redis에 세션이 계속 쌓인다.

## Implementation

- [ ] `app/session.py`의 `_sessions` dict를 Redis 클라이언트 호출로 교체 (`get`/`put` 시그니처 유지)
- [ ] 세션 키에 TTL 설정
- [ ] Redis 연결 정보를 설정(환경변수 등)으로 분리
- [ ] 테스트: 서버 3대 환경에서 로그인 후 다른 서버로 요청해도 세션이 유지되는지 확인
- [ ] 모니터링: Redis 가용성·메모리 사용량
- [x] 문서/설정 업데이트: `requirements.txt`에 `redis==5.0.8` 추가 (작업 트리 반영, 미커밋)

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 dict 기반 구현으로 되돌리고 `requirements.txt`에서 `redis`를 제거한다. 단, 서버 3대 구성에서는 로그인 풀림 문제가 다시 생긴다. Redis에 있던 세션은 옮겨지지 않으므로 롤백 시 사용자는 다시 로그인해야 한다.
- **Migration Cost:** Low

## References

- **Documentation:** `requirements.txt` (redis==5.0.8 추가, 미커밋 diff), `app/session.py`, 기준 커밋 919a937 (feat: 로그인/로그아웃 API)
