# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 로그인 세션 저장소를 프로세스 메모리(dict)에서 Redis로 옮긴다.
- **Scope:** member-portal / 세션 저장소 (`app/session.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장되어 각 서버 프로세스 메모리에만 존재한다. 서버를 3대로 늘리면 로그인한 서버와 다른 서버로 요청이 전달될 때 해당 세션을 찾지 못해 로그인이 풀린다.

### Constraints

- 서버 3대로 수평 확장한 상태에서 모든 인스턴스가 같은 세션을 조회할 수 있어야 한다.
- 기존 세션 모듈은 `get(session_id)` / `put(session_id, data)` 두 함수만 노출하고 있어, 호출부는 이 인터페이스에 의존한다.

## Decision

### Selected

- **Technology:** Redis, Python 클라이언트 `redis==5.0.8` (requirements.txt에 추가됨)
- **Architecture:** 각 앱 서버가 공유 Redis를 세션 저장소로 사용 (프로세스 로컬 상태 제거)
- **Implementation:** `app/session.py`의 `get`/`put` 시그니처는 유지하고 내부 저장소만 dict에서 Redis로 교체

## Rationale

1. 세션을 프로세스 외부의 공유 저장소에 두면 요청이 어느 서버로 가든 같은 세션을 조회할 수 있어, 다중 서버 환경의 로그인 풀림 문제가 해소된다.
2. 세션 모듈이 `get`/`put` 두 함수로 캡슐화되어 있어 호출부 변경 없이 저장소만 교체할 수 있다.

## Consequences

### Positive

- 서버 3대 간 세션이 공유되어 어느 인스턴스로 요청이 가도 로그인 상태가 유지된다.
- 앱 프로세스가 재시작·재배포되어도 세션이 사라지지 않는다.
- 서버를 추가로 늘릴 때 세션 관련 추가 작업이 필요 없다.

### Negative

- Redis라는 운영 대상 인프라가 하나 늘어난다.
- 세션 조회·저장마다 네트워크 왕복이 발생한다.
- 세션 데이터(dict)를 저장 시 직렬화/역직렬화해야 한다.

### Risks

- Redis 장애 시 모든 서버에서 세션 조회가 실패해 전체 로그인이 불가능해질 수 있다(단일 장애점).
- 전환 배포 시점에 기존 프로세스 메모리의 세션은 이관되지 않으므로 사용자가 한 번 재로그인해야 한다.
- 현재 dict 구현에는 만료가 없어, Redis에서 TTL을 설정하지 않으면 세션 키가 계속 누적된다.

## Implementation

- [ ] `app/session.py`의 `_sessions` dict를 Redis 클라이언트 기반 구현으로 교체 (`get`/`put` 시그니처 유지, 세션 데이터 직렬화, TTL 설정)
- [ ] Redis 접속 정보를 설정으로 분리
- [ ] 테스트: 서로 다른 인스턴스에서 `put` 후 `get`이 동일 세션을 반환하는지 검증
- [ ] 모니터링: Redis 가용성·연결 오류 알림
- [ ] 문서/설정 업데이트: 배포 환경에 Redis 추가, 전환 시 재로그인 발생 공지

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 dict 구현으로 되돌리고 requirements.txt에서 `redis`를 제거한다. 단, 다중 서버 환경에서는 로그인 풀림 문제가 다시 발생하며 Redis에 있던 세션은 소실된다.
- **Migration Cost:** Low

## References

- **Documentation:** `requirements.txt` (`redis==5.0.8` 추가, 미커밋), `app/session.py`, 관련 커밋 `ebd4778` (로그인/로그아웃 API)
