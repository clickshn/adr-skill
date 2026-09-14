# ADR-001: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 로그인 세션을 프로세스 메모리(dict) 대신 Redis에 저장해 여러 서버 인스턴스가 세션을 공유하도록 한다.
- **Scope:** member-portal / 세션 저장소 (`app/session.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 `dict`(`_sessions`)에 저장되어 각 프로세스 메모리에만 존재한다. 서버를 3대로 늘리면서 로그인한 서버가 아닌 다른 서버로 요청이 가면 세션을 찾지 못해 로그인이 풀리는 문제가 발생한다.

### Constraints

- 서버 3대가 동일한 세션을 조회할 수 있어야 한다.
- 기존 세션 인터페이스(`get(session_id)`, `put(session_id, data)`)를 호출하는 로그인/로그아웃 API(커밋 `2096563`)와 호환되어야 한다.
- 클라이언트는 `redis==5.0.8`(redis-py)을 사용한다(`requirements.txt`에 추가됨).

## Decision

### Selected

- **Technology:** Redis, Python 클라이언트 `redis==5.0.8`
- **Architecture:** 세션 상태를 애플리케이션 프로세스 밖의 공유 Redis로 옮겨, 3대의 서버가 모두 같은 저장소를 읽고 쓰는 구조로 바꾼다. 애플리케이션 서버는 세션 측면에서 무상태가 된다.
- **Implementation:** `app/session.py`의 `get`/`put` 시그니처는 유지하고 내부 저장을 `_sessions` dict에서 Redis 호출로 교체한다. 세션 `dict`는 직렬화해서 `session_id` 키로 저장한다.

## Rationale

1. 세션이 서버 간에 공유되지 않는 것이 로그인 풀림의 직접 원인이므로, 모든 서버가 접근하는 외부 저장소로 옮기면 어느 서버로 요청이 가도 같은 세션을 조회할 수 있다.
2. 세션 모듈의 인터페이스가 `get`/`put` 두 함수로 작아서 호출부 변경 없이 저장소만 교체할 수 있다.
3. 세션은 키-값 형태이므로 키-값 저장소인 Redis와 잘 맞는다.

## Consequences

### Positive

- 서버 3대 중 어느 서버로 요청이 가도 로그인 상태가 유지된다.
- 서버를 추가하거나 재시작해도 세션이 사라지지 않는다.

### Negative

- Redis라는 운영 대상 인프라가 하나 늘어난다.
- 세션 조회/저장마다 네트워크 왕복이 생긴다(기존에는 메모리 접근).
- 세션 데이터를 직렬화할 수 있는 형태로 유지해야 한다.

### Risks

- Redis 장애 시 3대 서버 모두에서 세션 조회가 실패하므로 Redis가 단일 장애점이 된다.
- 전환 시점에 프로세스 메모리에 있던 기존 세션은 이전되지 않아 사용자가 한 번 재로그인해야 한다.
- 현재 `app/session.py`에는 만료·삭제 로직이 없어 그대로 옮기면 Redis에 세션 키가 무기한 쌓인다.

## Implementation

- [ ] `app/session.py`의 저장 로직을 Redis로 교체 (`get`/`put` 시그니처 유지)
- [ ] 세션 TTL 설정과 로그아웃용 삭제 함수 추가
- [ ] Redis 접속 정보(호스트/포트/인증)를 설정으로 분리
- [ ] 테스트: 서버 여러 대 환경에서 다른 인스턴스로 요청해도 로그인이 유지되는지 확인
- [ ] 모니터링: Redis 가용성·연결 오류 알림
- [ ] 문서/설정 업데이트: 배포 환경에 Redis 추가

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 dict 기반 구현으로 되돌리고 `requirements.txt`에서 `redis`를 제거한다. 단, 서버가 여러 대인 동안에는 로그인 풀림 문제가 다시 생긴다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py`, `requirements.txt` (`redis==5.0.8` 추가, 미커밋), 관련 커밋 `2096563` (로그인/로그아웃 API)
