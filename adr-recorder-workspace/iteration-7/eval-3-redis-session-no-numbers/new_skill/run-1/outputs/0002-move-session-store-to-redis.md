# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 세션 저장소를 프로세스 메모리(dict)에서 Redis로 옮겨 여러 서버가 세션을 공유하게 한다.
- **Scope:** member-portal / 세션 저장소 (app/session.py)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장되어 각 프로세스 메모리에만 존재한다. 서버를 3대로 늘리면 로그인 요청을 처리한 서버와 이후 요청을 받는 서버가 달라질 수 있고, 다른 서버에는 해당 세션이 없어 로그인이 풀린다.

### Constraints

- 서버 3대로 수평 확장한 구성에서 모든 인스턴스가 같은 세션을 조회할 수 있어야 한다.
- 기존 세션 모듈은 `get(session_id)` / `put(session_id, data)` 두 함수로 된 dict 기반 인터페이스이며, 로그인/로그아웃 API(커밋 919a937)가 이 모듈에 의존한다.
- 스택은 FastAPI 0.112.2 + uvicorn 0.30.6이며, 클라이언트 라이브러리는 `redis==5.0.8`로 고정되어 requirements.txt에 추가되었다(미커밋 변경).

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 세션 상태를 각 서버 프로세스 밖의 공유 Redis 저장소에 두고, 3대의 앱 서버가 모두 이를 조회·기록한다.
- **Implementation:** `app/session.py`의 `get`/`put` 시그니처는 유지하고 내부 저장소만 dict에서 Redis로 교체한다. 현재 저장소에는 requirements.txt 변경만 반영되어 있고 `app/session.py`는 아직 dict 기반이다.

## Rationale

1. 프로세스 메모리 세션은 인스턴스 간에 공유되지 않아, 서버를 3대로 늘리면 로그인이 풀리는 문제가 생긴다.
2. 세션을 외부 공유 저장소(Redis)에 두면 요청이 어느 서버로 가든 같은 세션을 조회할 수 있다.

## Alternatives

### 현행 유지 (프로세스 메모리 dict)

- **Pros:** 별도 인프라 없이 동작하며, 현재 코드(`app/session.py`) 그대로다.
- **Cons:** 세션이 프로세스마다 따로 존재해 여러 서버 간에 공유되지 않는다.
- **Rejected because:** 서버를 3대로 늘리면 다른 서버로 간 요청에서 세션을 찾지 못해 로그인이 풀린다.

## Consequences

### Positive

- 서버 3대 구성에서도 어느 인스턴스로 요청이 가든 로그인 상태가 유지된다.
- 앱 서버 재시작·재배포 시 프로세스 메모리와 함께 세션이 사라지지 않는다.

### Negative

- 운영해야 할 인프라(Redis 서버)가 하나 늘어난다.
- 세션 조회·기록마다 네트워크 왕복이 생기고, 세션 데이터(dict)를 직렬화해 저장해야 한다.

### Risks

- Redis가 로그인 경로의 단일 장애 지점이 된다. Redis 장애 시 3대 모두에서 세션 조회가 실패한다.
- 현재 dict 구현에는 만료 개념이 없어, TTL을 정하지 않고 옮기면 Redis에 세션이 무한히 쌓일 수 있다.

## Implementation

- [ ] 구현 작업: `app/session.py`의 `get`/`put`을 Redis 기반으로 교체(requirements.txt에 `redis==5.0.8` 추가는 완료, 미커밋)
- [ ] 테스트: 서로 다른 인스턴스에서 로그인 후 조회 시 세션이 유지되는지 검증
- [ ] 모니터링: Redis 가용성·메모리 사용량 모니터링
- [ ] 문서/설정 업데이트: Redis 접속 정보(호스트·포트 등) 설정 추가 — 현재 저장소에는 해당 설정이 없다

## Reversibility

- **Reversible:** Partial
- **Rollback:** `app/session.py`를 dict 구현으로 되돌리고 requirements.txt에서 `redis` 줄을 제거한다. 코드 롤백은 간단하지만, 서버 3대 구성을 유지하는 한 로그인이 풀리는 원래 문제가 재발하므로 서버를 1대로 줄이지 않으면 실질적으로 되돌릴 수 없다.
- **Migration Cost:** Low

## References

- **Documentation:** requirements.txt (`redis==5.0.8` 추가, 미커밋), app/session.py, 커밋 919a937 (feat: 로그인/로그아웃 API)
