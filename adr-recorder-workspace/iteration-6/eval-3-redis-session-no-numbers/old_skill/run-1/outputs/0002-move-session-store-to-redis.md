# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 세션 저장소를 프로세스 메모리(dict)에서 Redis로 옮겨 여러 서버 인스턴스가 세션을 공유하게 한다.
- **Scope:** member-portal / 세션 저장소 (app/session.py)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장되어 각 프로세스 메모리에만 존재한다.
서버를 3대로 늘리면 로그인을 처리한 서버가 아닌 다른 서버로 요청이 가면 세션을 찾지 못해 로그인이 풀린다.
현재 구현에는 세션 만료(TTL) 처리가 없고 프로세스가 재시작되면 모든 세션이 사라진다.

### Constraints

- 서버 3대로 수평 확장한 상태에서 어느 인스턴스로 요청이 가도 같은 세션을 읽을 수 있어야 한다.
- 기존 세션 모듈의 `get(session_id)` / `put(session_id, data)` 인터페이스를 쓰는 로그인/로그아웃 코드가 있다.
- Python 클라이언트로 `redis==5.0.8`을 requirements.txt에 추가했다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 3대의 앱 서버가 하나의 공유 Redis를 세션 저장소로 쓴다. 앱 서버는 세션 상태를 갖지 않는다(stateless).
- **Implementation:** `app/session.py`의 `get`/`put` 시그니처는 유지하고 내부 저장소만 dict에서 Redis 호출로 바꾼다.

## Rationale

1. 세션을 프로세스 밖의 공유 저장소에 두면 요청이 어느 서버로 가도 같은 세션을 읽을 수 있어 확장 후 로그인이 풀리는 문제가 해결된다.
2. 세션 모듈이 `get`/`put` 두 함수로 격리되어 있어 호출부를 고치지 않고 저장소만 바꿀 수 있다.

## Consequences

### Positive

- 앱 서버가 세션 상태를 갖지 않아 서버 수를 늘리거나 줄여도 로그인 상태가 유지된다.
- 앱 프로세스가 재시작되거나 배포되어도 세션이 사라지지 않는다.
- Redis 키 만료 기능으로 현재 없는 세션 만료를 구현할 수 있다.

### Negative

- 운영해야 할 인프라 구성 요소(Redis)가 하나 늘어난다.
- 세션 조회마다 네트워크 왕복이 생겨 메모리 조회보다 느려진다.
- 세션 데이터(dict)를 Redis에 저장하려면 직렬화가 필요하다.

### Risks

- Redis 장애 시 모든 서버에서 세션 조회가 실패해 전체 로그인이 불가능해진다(단일 장애점).
- Redis 전환 배포 시점에 기존 메모리 세션은 이관되지 않아 기존 로그인 사용자는 다시 로그인해야 한다.
- 세션에 개인정보·인증 정보가 담기므로 Redis 접근 제어·네트워크 노출 설정이 미흡하면 세션 탈취 위험이 있다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체(직렬화, 세션 TTL 포함)
- [ ] 로그아웃 시 세션 삭제 경로 확인
- [ ] 여러 인스턴스 간 세션 공유 테스트(서버 A에서 로그인 후 서버 B로 요청)
- [ ] Redis 연결 실패·지연 모니터링 및 알림
- [ ] Redis 접속 정보(호스트, 인증)를 환경 설정으로 분리하고 배포 설정에 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 dict 기반 구현으로, requirements.txt에서 `redis` 줄을 되돌리면 된다. 단, 서버 3대 구성에서 되돌리면 로그인이 풀리는 문제가 다시 생기므로 단일 서버로 줄이거나 sticky session을 함께 적용해야 한다. 롤백 시 Redis에 있던 세션은 사라져 사용자는 다시 로그인해야 한다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py` (현재 dict 기반 세션 저장소, 커밋 69b2c22), `requirements.txt` (`redis==5.0.8` 추가, 미커밋)
