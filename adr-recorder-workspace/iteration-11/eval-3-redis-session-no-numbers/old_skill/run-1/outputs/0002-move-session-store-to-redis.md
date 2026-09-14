# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 로그인 세션 저장소를 프로세스 메모리(dict)에서 Redis로 옮긴다.
- **Scope:** member-portal / 세션 저장소 (app/session.py)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장되어 각 서버 프로세스 메모리에만 존재한다. 서버를 3대로 늘리면서, 로그인한 서버가 아닌 다른 서버로 요청이 가면 세션을 찾지 못해 로그인이 풀리는 문제가 생긴다.

### Constraints

- 서버 3대가 같은 세션을 조회할 수 있어야 한다(세션이 특정 프로세스에 묶이면 안 된다).
- 기존 세션 모듈 인터페이스는 `get(session_id)` / `put(session_id, data)` 두 함수뿐이다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`, requirements.txt에 추가됨)
- **Architecture:** 세션을 각 서버 프로세스 메모리 대신 모든 서버가 공유하는 외부 Redis에 저장한다.
- **Implementation:** `app/session.py`의 `get`/`put`을 Redis 조회·저장으로 교체한다. 현재 코드는 아직 dict 기반이다.

## Rationale

1. 세션을 서버 밖 공유 저장소에 두면 요청이 어느 서버로 가든 같은 세션을 읽을 수 있어, 서버 3대 환경에서 로그인이 풀리는 문제가 해소된다.

## Alternatives

### 현행 유지: 프로세스 메모리(dict) 세션 저장소

- **Pros:** 외부 의존성이 없고 구현이 단순하다.
- **Cons:** 세션이 해당 프로세스에만 존재해 서버 간에 공유되지 않는다.
- **Rejected because:** 서버를 3대로 늘리면 다른 서버로 간 요청에서 세션을 찾지 못해 로그인이 풀린다.

## Consequences

### Positive

- 서버 대수와 무관하게 세션이 유지되어 수평 확장이 가능해진다.
- 서버 프로세스 재시작 시에도 세션이 사라지지 않는다.

### Negative

- Redis라는 운영 대상 인프라와 의존성이 하나 늘어난다.
- 세션 조회·저장마다 네트워크 왕복이 추가된다.

### Risks

- Redis 장애 시 모든 서버에서 세션 조회·로그인이 함께 실패할 수 있다.
- 세션 데이터(dict)를 Redis에 넣으려면 직렬화가 필요하다.

## Implementation

- [x] requirements.txt에 `redis==5.0.8` 추가
- [ ] 구현 작업: `app/session.py`의 `get`/`put`을 Redis 기반으로 교체
- [ ] 테스트: 서로 다른 서버(프로세스)에서 같은 세션이 조회되는지 확인
- [ ] 모니터링: Redis 가용성 모니터링
- [ ] 문서/설정 업데이트: Redis 접속 정보 설정 추가

## Reversibility

- **Reversible:** Yes
- **Rollback:** requirements.txt에서 `redis`를 제거하고 `app/session.py`를 dict 기반 구현으로 되돌린다. 롤백 시 Redis에 저장된 세션은 사라져 사용자가 다시 로그인해야 하고, 다중 서버 환경에서는 로그인 풀림 문제가 재발한다.
- **Migration Cost:** Low

## References

- **Documentation:** 현행 구현 `app/session.py` (커밋 0c08f5e에서 도입), 의존성 변경 `requirements.txt` (미커밋)
