# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 세션 저장소를 각 프로세스의 메모리(dict)에서 모든 서버가 공유하는 Redis로 옮긴다.
- **Scope:** member-portal / 세션 저장소 (`app/session.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 dict `_sessions`에 들어 있어서, 세션이 그것을 만든 프로세스 안에만 존재한다. 서버를 3대로 늘리면 로그인 요청을 처리한 서버와 다른 서버로 다음 요청이 가는 순간 세션을 찾지 못해 로그인이 풀린다.

### Constraints

- 서버 3대 구성에서 어느 서버가 요청을 받든 같은 세션을 읽을 수 있어야 한다.
- 세션 접근 인터페이스는 `get(session_id)` / `put(session_id, data)` 두 함수뿐이라, 교체 범위는 `app/session.py` 하나로 한정된다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`, `requirements.txt`에 추가됨)
- **Architecture:** 세션 상태를 앱 프로세스 밖의 공유 저장소(Redis)로 옮기고, 앱 서버들은 세션 상태를 갖지 않는다.
- **Implementation:** `app/session.py`의 `get`/`put` 시그니처는 그대로 두고 내부 저장소만 dict에서 Redis로 바꾼다. 현재 의존성만 추가되어 있고, 코드는 아직 바뀌지 않았다.

## Rationale

1. 세션을 세 서버가 공유하는 한 저장소에 두면, 요청이 어느 서버로 가도 같은 세션이 조회되어 로그인이 유지된다.

## Consequences

### Positive

- 인스턴스 간 세션이 공유되어 서버 수를 늘려도 로그인 상태가 유지된다.
- 앱 서버를 재시작하거나 재배포해도 세션이 사라지지 않는다.

### Negative

- Redis라는 운영 대상 인프라가 하나 늘어난다(배포, 접속 설정, 모니터링).
- 세션을 조회·저장할 때마다 메모리 접근 대신 네트워크 왕복이 생긴다.
- 세션 값(현재 `dict`)을 저장하려면 직렬화/역직렬화가 필요하다.

### Risks

- Redis가 죽거나 연결이 끊기면 모든 서버에서 로그인·세션 조회가 동시에 실패한다.
- 만료(TTL)를 설정하지 않으면 세션 키가 계속 쌓여 Redis 메모리가 늘어난다(현재 dict 구현에도 만료가 없다).
- 전환 배포 시점에 메모리에 있던 기존 세션은 옮겨지지 않으므로 사용자가 한 번 다시 로그인해야 한다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체 (직렬화, 세션 TTL 포함)
- [ ] 테스트: 여러 인스턴스를 띄운 상태에서 로그인 후 다른 인스턴스로 요청해도 세션이 유지되는지 확인
- [ ] 모니터링: Redis 연결 오류, 메모리 사용량, 키 개수
- [ ] 문서/설정 업데이트: Redis 접속 정보를 환경 변수로 분리하고 배포 설정에 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 dict 구현으로 되돌리고 `requirements.txt`에서 `redis==5.0.8`를 제거한다. Redis에 있던 세션은 소실되어 재로그인이 필요하고, 서버 3대 구성에서는 로그인 풀림 문제가 다시 생긴다.
- **Migration Cost:** Low

## References

- **Documentation:** `requirements.txt` (`redis==5.0.8` 추가, 미커밋, 기준 커밋 `ba84cb2`), `app/session.py`
