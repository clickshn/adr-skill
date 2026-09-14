# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 프로세스 메모리 딕셔너리에서 Redis로 옮긴다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

세션이 `app/session.py`의 프로세스 메모리 딕셔너리(`_sessions`)에 저장되어 각 서버 프로세스에만 존재한다. 서버를 3대로 늘리면서 요청이 다른 서버로 분산되면 해당 서버에 세션이 없어 로그인이 풀리는 문제가 발생했다.

### Constraints

- 서버 인스턴스가 3대로 늘어난 상태이므로 세션은 인스턴스 간에 공유되어야 한다.
- 현재 세션 접근은 `app/session.py`의 `get`/`put` 두 함수로 격리되어 있어 교체 지점이 좁다.
- 기존 스택은 FastAPI + uvicorn + SQLAlchemy이며, 별도의 공유 저장소는 아직 없다.

## Decision

### Selected

- **Technology:** Redis (`redis==5.0.8`, requirements.txt에 추가됨)
- **Architecture:** 세션을 프로세스 로컬 메모리가 아닌 외부 공유 저장소에 두어, 3대의 서버 인스턴스가 동일한 세션을 조회·갱신하도록 한다.
- **Implementation:** `app/session.py`의 `get`/`put` 구현을 Redis 클라이언트 호출로 교체한다. 호출부 인터페이스는 그대로 유지한다.

## Rationale

1. 세션이 프로세스에 묶여 있는 것이 로그인 풀림의 직접 원인이므로, 인스턴스 밖의 공유 저장소로 옮기면 해결된다.
2. 세션 접근이 `get`/`put` 두 함수로 이미 격리되어 있어 저장소 교체 범위가 작다.
3. 의존성은 이미 requirements.txt에 반영되어 있어(`redis==5.0.8`) 도입 준비가 되어 있다.

## Alternatives

### 현행 유지 (프로세스 메모리 세션)

- **Pros:** 추가 인프라와 의존성이 필요 없다.
- **Cons:** 세션이 프로세스마다 따로 존재한다.
- **Rejected because:** 서버를 3대로 늘린 뒤 요청이 다른 인스턴스로 가면 로그인이 풀린다.

## Consequences

### Positive

- 어느 인스턴스가 요청을 받아도 동일한 세션을 볼 수 있어 로그인 풀림이 해소된다.
- 서버 인스턴스를 더 늘려도 세션 관점의 추가 작업이 필요 없다.

### Negative

- Redis라는 외부 컴포넌트가 운영 대상에 추가된다(배포·설정·접속 정보 관리).
- 세션 조회가 인프로세스 딕셔너리 조회에서 네트워크 호출로 바뀐다.

### Risks

- Redis 장애 시 전체 인스턴스의 로그인이 동시에 영향을 받는다(단일 장애점).
- 세션 데이터 직렬화 방식과 만료(TTL) 정책이 아직 정해지지 않았다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체
- [ ] 3대 인스턴스 환경에서 로그인 유지 테스트 (인스턴스 간 요청 분산 시나리오)
- [ ] Redis 연결 상태·에러율 모니터링 추가
- [ ] Redis 접속 설정(호스트/포트/자격증명) 배포 설정에 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 커밋 bd074f7 시점의 메모리 딕셔너리 구현으로 되돌리고 requirements.txt에서 `redis==5.0.8` 줄을 제거한다. 단 롤백 시 저장 중이던 활성 세션은 유지되지 않는다(재로그인 필요).
- **Migration Cost:** Low

## References

- **Documentation:** requirements.txt (`+redis==5.0.8`), app/session.py
