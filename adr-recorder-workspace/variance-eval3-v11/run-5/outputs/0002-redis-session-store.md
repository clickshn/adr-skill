# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 프로세스 메모리 딕셔너리에서 외부 Redis로 옮긴다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

세션은 현재 애플리케이션 프로세스 안의 딕셔너리에 보관된다(`app/session.py`의 `_sessions`). 서버를 3대로 늘리면서 요청이 세션을 만든 서버가 아닌 다른 서버로 가면 세션을 찾지 못해 로그인이 풀리는 문제가 발생한다.

### Constraints

- 서버는 3대로 운영되며, 어느 서버가 요청을 받아도 동일한 세션을 읽을 수 있어야 한다.
- 기존 스택은 FastAPI + uvicorn + SQLAlchemy이며, 세션 접근 인터페이스는 `get`/`put` 두 함수로 단순하다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`을 `requirements.txt`에 추가)
- **Architecture:** 세션을 애플리케이션 프로세스 외부의 공유 저장소에 두어, 3대의 서버가 동일한 세션 상태를 참조하도록 한다.
- **Implementation:** `app/session.py`의 `get`/`put` 구현을 프로세스 메모리 딕셔너리 대신 Redis 읽기/쓰기로 교체한다. 호출부 인터페이스는 유지한다.

## Rationale

1. 세션이 프로세스 밖의 공유 저장소에 있으면 요청이 어느 서버로 분배되어도 동일한 세션을 조회할 수 있어, 서버 증설로 발생한 로그인 풀림의 원인이 제거된다.
2. 세션 접근 지점이 `app/session.py`의 `get`/`put` 두 함수뿐이라 저장소 교체 범위가 좁다.

## Alternatives

### 프로세스 메모리 유지(현행)

- **Pros:** 추가 인프라 구성요소가 없고, 조회에 네트워크 홉이 없다.
- **Cons:** 세션이 서버 인스턴스에 묶여 있어 수평 확장과 양립하지 않는다. 프로세스 재시작 시 세션이 사라진다.
- **Rejected because:** 서버를 3대로 늘린 뒤 로그인이 풀리는 문제가 실제로 발생했다.

## Consequences

### Positive

- 서버 대수와 무관하게 세션이 공유되어 로그인 유지 문제가 해소된다.
- 프로세스 재시작·재배포 후에도 세션이 유지된다.

### Negative

- 운영해야 할 외부 구성요소(Redis)가 하나 늘어난다.
- 세션 조회마다 네트워크 왕복이 생기고, 세션 데이터를 직렬화/역직렬화해야 한다.

### Risks

- Redis가 단일 장애점이 된다. Redis 장애 시 전 사용자 인증이 동시에 실패할 수 있다.
- 전환 시점에 프로세스 메모리에 있던 기존 세션은 이어지지 않으므로, 사용자가 한 번 로그아웃된다.

## Implementation

- [ ] 구현 작업: `app/session.py`를 Redis 클라이언트 기반으로 교체(키 네임스페이스, 세션 TTL 정의 포함)
- [ ] 테스트: 서로 다른 인스턴스에서 쓰고 읽는 세션 공유 시나리오 검증
- [ ] 모니터링: Redis 연결 실패/지연, 세션 조회 오류율 관측
- [ ] 문서/설정 업데이트: Redis 접속 설정(환경변수) 및 배포 구성 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 프로세스 메모리 딕셔너리 구현(현재 HEAD인 `bd074f7` 시점 상태)으로 되돌리고 `requirements.txt`에서 `redis==5.0.8`을 제거한다. 되돌리면 서버 3대 환경의 로그인 풀림 문제는 다시 발생한다.
- **Migration Cost:** Low

## References

- **Documentation:** `requirements.txt`(`redis==5.0.8` 추가), `app/session.py`
