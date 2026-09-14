# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 각 서버 프로세스 메모리(dict)에서 서버끼리 공유하는 Redis로 옮긴다.
- **Scope:** member-portal / 세션 저장소 (`app/session.py`)
- **Decision Source:** Human

---

## Context

### Problem

서버를 3대로 늘린 뒤 로그인이 풀리는 문제가 생긴다. 지금은 세션을 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장한다. 그래서 세션이 그 프로세스 안에만 있고, 로그인한 서버가 아닌 다른 서버로 요청이 가면 세션을 찾지 못한다.

### Constraints

- 서버 3대 모두가 같은 세션을 조회·저장할 수 있어야 한다.
- 세션 모듈은 `get(session_id)`와 `put(session_id, data: dict)` 두 함수만 노출하고, 세션 값은 dict다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`, requirements.txt에 추가됨)
- **Architecture:** 세션을 각 프로세스 메모리가 아니라 서버 3대가 함께 접근하는 외부 저장소(Redis)에 저장한다.
- **Implementation:** `app/session.py`의 `get`/`put`이 쓰는 저장소를 Redis로 교체한다. 지금은 의존성만 추가됐고(requirements.txt, 미커밋) 코드는 아직 dict 기반이다.

## Rationale

1. 프로세스 메모리 세션은 서버마다 따로 있어서 다중 서버 환경에서 공유되지 않는다. 서버 3대 증설 후 로그인이 풀리는 원인이 이것이다. 세션을 외부 공유 저장소로 옮기면 어느 서버로 요청이 가도 같은 세션을 조회할 수 있다.

## Alternatives

### 현행 유지 (프로세스 메모리 세션)

- **Pros:** 별도 저장소나 의존성 없이 동작한다(현재 구현).
- **Cons:** 세션이 프로세스마다 따로 있어서 서버끼리 공유되지 않는다.
- **Rejected because:** 서버 3대 구성에서 다른 서버로 요청이 가면 로그인이 풀린다.

## Consequences

### Positive

- 서버 3대 중 어느 서버로 요청이 가도 같은 세션을 조회해서 로그인이 유지된다.

### Negative

- 운영해야 할 외부 서비스(Redis)와 새 의존성(`redis`)이 늘어난다.

### Risks

- Redis에 접속할 수 없으면 모든 서버에서 세션 조회와 저장이 실패한다.
- 전환 배포 때 프로세스 메모리에 있던 기존 세션은 옮겨지지 않는다. 그 시점에 로그인해 있던 사용자는 다시 로그인해야 한다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체 (세션 값이 dict라서 직렬화 방식을 정해야 함)
- [ ] 세션 만료 정책 결정 (현재 dict 구현에는 만료가 없음)
- [ ] 테스트: 한 서버에서 로그인한 세션이 다른 서버로 간 요청에서도 유지되는지 확인
- [ ] 모니터링: Redis 연결 실패와 가용성
- [ ] 문서/설정 업데이트: Redis 접속 정보 설정 추가

## Reversibility

- **Reversible:** Partial
- **Rollback:** requirements.txt에서 `redis==5.0.8`을 빼고 `app/session.py`를 커밋 `0c08f5e`의 dict 구현으로 되돌리면 코드는 원래대로 돌아간다. 하지만 서버 3대 구성에서는 로그인이 풀리는 원래 문제가 다시 생긴다. 서버를 1대로 줄이지 않으면 실제로 쓸 수 있는 롤백이 아니다.
- **Migration Cost:** Low

## References

- **Documentation:** 커밋 `0c08f5e` (member-portal 초기 구성: `app/session.py`의 프로세스 메모리 세션 저장소를 도입한 커밋, `git show --stat`로 확인)
