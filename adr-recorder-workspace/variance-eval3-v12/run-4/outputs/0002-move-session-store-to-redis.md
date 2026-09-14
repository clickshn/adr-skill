# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 애플리케이션 프로세스 메모리 딕셔너리에서 외부 Redis로 옮긴다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

`app/session.py`의 세션 저장소는 프로세스 내부 딕셔너리(`_sessions`)로 구현되어 있어 인스턴스마다 세션이 따로 존재한다. 서버를 3대로 늘리면서 로그인한 사용자의 후속 요청이 다른 인스턴스로 분산되면 해당 인스턴스에는 세션이 없어 로그인이 풀리는 문제가 관찰되었다.

### Constraints

- 서버 인스턴스 3대가 동일한 세션을 공유해야 한다.
- 기존 스택은 FastAPI + uvicorn + SQLAlchemy이며, 세션 조회/저장 인터페이스(`get`/`put`)는 유지하는 편이 변경 범위가 작다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`, requirements.txt에 추가 완료)
- **Architecture:** 프로세스 로컬 인메모리 저장소를 외부 공유 세션 스토어로 분리한다. 애플리케이션 인스턴스는 상태를 갖지 않고, 모든 인스턴스가 동일한 Redis를 바라본다.
- **Implementation:** `app/session.py`의 `get`/`put` 시그니처는 유지한 채 내부 구현만 Redis 읽기/쓰기로 교체한다. 현재 requirements.txt만 수정된 상태이고 `app/session.py`는 아직 딕셔너리 구현이다.

## Rationale

1. 세션을 프로세스 밖으로 빼야 인스턴스 수와 무관하게 로그인 상태가 유지된다. 이것이 이번 문제의 직접적인 원인 제거다.
2. 저장소 접근 지점이 `app/session.py`의 `get`/`put` 두 함수로 이미 격리되어 있어, 호출부 변경 없이 구현만 교체할 수 있다.
3. Redis는 세션처럼 짧은 수명의 키-값 데이터에 적합하고 TTL로 만료를 위임할 수 있다.

## Alternatives

### 프로세스 메모리 세션 저장소 유지 (현행)

- **Pros:** 외부 의존성이 없고 구현이 가장 단순하다. 네트워크 왕복이 없다.
- **Cons:** 세션이 인스턴스에 묶여 수평 확장이 불가능하고, 프로세스 재시작 시 전체 세션이 사라진다.
- **Rejected because:** 서버를 3대로 늘리자 요청이 다른 인스턴스로 갈 때 로그인이 풀리는 문제가 실제로 발생했다.

## Consequences

### Positive

- 인스턴스 수를 늘려도 로그인 상태가 유지되고, 애플리케이션이 무상태에 가까워져 배포·재시작 시 세션이 보존된다.

### Negative

- 운영해야 할 구성 요소(Redis 인스턴스, 접속 설정, 인증 정보)가 늘어난다.
- 세션 조회마다 네트워크 호출이 생겨 인메모리 조회보다 지연이 증가한다.

### Risks

- Redis가 단일 장애점이 된다. 장애 시 전체 로그인이 영향을 받는다.
- 기존에 프로세스 메모리에 있던 세션은 전환 시점에 소실되어 사용자가 한 번 재로그인해야 한다.
- 세션 값 직렬화 방식(현재 `dict`)을 정해야 하며, 만료 정책(TTL)이 없으면 키가 무한히 쌓인다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체하고 세션 TTL을 설정
- [ ] Redis 접속 설정(호스트/포트/인증)을 환경변수로 외부화
- [ ] 인스턴스 3대 환경에서 로그인 후 요청이 분산돼도 세션이 유지되는지 테스트
- [ ] Redis 가용성·연결 실패·메모리 사용량 모니터링 추가
- [ ] 로컬/배포 환경의 Redis 구동 방법 문서화

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 딕셔너리 기반 구현으로 되돌리고 requirements.txt에서 `redis==5.0.8`을 제거한다. 되돌리면 다중 인스턴스 문제가 다시 발생하므로 서버를 1대로 축소하는 것이 전제다.
- **Migration Cost:** Low

## References

- **Documentation:** app/session.py, requirements.txt
