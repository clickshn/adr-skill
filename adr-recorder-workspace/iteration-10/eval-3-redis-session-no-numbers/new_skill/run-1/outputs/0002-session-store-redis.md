# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 세션 저장소를 프로세스 메모리(dict)에서 Redis로 옮겨 여러 서버가 세션을 공유하게 한다.
- **Scope:** member-portal / 세션 저장소 (app/session.py)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장되어 각 서버 프로세스 메모리에만 존재한다. 서버를 3대로 늘리면 로그인한 서버가 아닌 다른 서버로 요청이 가면 세션을 찾지 못해 로그인이 풀린다.

### Constraints

- 서버 3대(수평 확장) 환경에서 모든 인스턴스가 같은 세션을 조회할 수 있어야 한다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`, requirements.txt에 추가됨)
- **Architecture:** 세션 데이터를 프로세스 밖 공유 저장소(Redis)에 두고 3대 서버가 함께 읽고 쓴다.
- **Implementation:** `app/session.py`의 `get`/`put`을 Redis 기반으로 교체한다. (현재는 의존성만 추가되었고 코드는 아직 dict 기반)

## Rationale

1. 세션을 개별 프로세스가 아닌 공유 저장소에 두면 요청이 어느 서버로 가도 같은 세션을 조회할 수 있어, 서버 3대 증설 시 로그인이 풀리는 문제가 해소된다.

## Alternatives

### 프로세스 메모리 유지 (현행)

- **Pros:** 별도 인프라나 외부 의존성 없이 동작한다 (현재 구현).
- **Cons:** 세션이 서버마다 따로 저장되어 인스턴스 간에 공유되지 않는다.
- **Rejected because:** 서버를 3대로 늘리면 다른 서버로 간 요청에서 로그인이 풀린다.

## Consequences

### Positive

- 서버 3대가 세션을 공유해 어느 서버로 요청이 가도 로그인 상태가 유지된다.
- 애플리케이션 프로세스를 재시작해도 세션이 사라지지 않는다.

### Negative

- Redis라는 운영 대상 인프라가 하나 늘어난다.
- 세션 조회·저장마다 네트워크 왕복이 추가된다.

### Risks

- Redis 장애 시 모든 서버에서 세션 조회가 실패해 전체 로그인이 영향을 받는다(단일 장애점).
- 현재 dict 구현에는 세션 만료가 없어, 그대로 옮기면 Redis에 세션 키가 계속 쌓인다.
- 전환 배포 시점에 기존 프로세스 메모리 세션은 옮겨지지 않아 접속 중인 사용자가 한 번 다시 로그인해야 한다.

## Implementation

- [x] requirements.txt에 `redis==5.0.8` 추가
- [ ] `app/session.py`의 `get`/`put`을 Redis 클라이언트 기반으로 교체 (세션 dict 직렬화 포함)
- [ ] 테스트: 서로 다른 서버 인스턴스에서 `put`한 세션을 `get`으로 조회할 수 있는지 확인
- [ ] 모니터링: Redis 연결 상태·가용성 모니터링
- [ ] 문서/설정 업데이트: Redis 접속 정보 설정 추가

## Reversibility

- **Reversible:** Yes
- **Rollback:** requirements.txt에서 `redis`를 제거하고 `app/session.py`를 dict 기반 구현으로 되돌린다. 단, 서버가 여러 대인 상태로 되돌리면 로그인이 풀리는 문제가 다시 생긴다.
- **Migration Cost:** Low

## References

- **Documentation:** requirements.txt (`redis==5.0.8` 추가, 미커밋 변경), app/session.py
