# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 각 프로세스의 인메모리 dict에서 모든 인스턴스가 공유하는 Redis로 옮긴다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

세션이 애플리케이션 프로세스 메모리에 저장되어 있다(`app/session.py`의 모듈 전역 `_sessions` dict).
서버를 3대로 늘리면서 같은 사용자의 요청이 다른 인스턴스로 라우팅되면 그 인스턴스에는 세션이
없어 로그인이 풀리는 문제가 발생하고 있다. 프로세스 재시작 시에도 세션이 전부 사라진다.

### Constraints

- 인스턴스 3대가 공통으로 읽고 쓸 수 있는 세션 저장소가 필요하다.
- 세션 접근이 `app/session.py`의 `get`/`put` 두 함수로만 이루어져 있어 교체 범위가 이 모듈로 한정된다.
- 기존 스택은 FastAPI + uvicorn + SQLAlchemy이며, 의존성은 `requirements.txt`로 관리한다.

## Decision

### Selected

- **Technology:** Redis (`redis==5.0.8`, `requirements.txt`에 추가됨)
- **Architecture:** 프로세스 로컬 인메모리 저장소 → 전 인스턴스가 공유하는 외부 세션 저장소
- **Implementation:** `app/session.py`의 `get`/`put` 시그니처는 유지한 채 내부 구현만 Redis 클라이언트 호출로 교체한다. 호출부는 수정하지 않는다.

## Rationale

1. 세션을 프로세스 밖으로 빼면 요청이 3대 중 어느 인스턴스로 가더라도 같은 세션을 읽을 수 있어, 로그인이 풀리는 직접 원인이 제거된다.
2. 세션 접근이 `get`/`put` 두 함수로 캡슐화되어 있어 호출부 변경 없이 저장소 백엔드만 바꿀 수 있다.
3. 세션이 프로세스 수명과 분리되므로 배포·재시작 시의 세션 유실도 함께 해소된다.

## Alternatives

### 프로세스 메모리 세션 유지 (현행)

- **Pros:** 추가 인프라와 운영 부담이 없고, 세션 조회에 네트워크 왕복이 없다.
- **Cons:** 세션이 개별 인스턴스에 묶여 공유되지 않는다.
- **Rejected because:** 서버를 3대로 늘리면서 요청이 다른 인스턴스로 갈 때 세션을 찾지 못해 로그인이 풀리는 문제가 실제로 발생했다.

## Consequences

### Positive

- 인스턴스 수와 무관하게 세션이 유지되어 수평 확장 경로가 열린다.
- 배포·프로세스 재시작 시 세션이 사라지지 않는다.

### Negative

- 운영·모니터링 대상이 되는 외부 의존성이 하나 늘어난다.
- 세션 조회·저장마다 네트워크 왕복이 생긴다.
- Redis 접속 정보와 자격 증명을 환경별로 관리해야 한다.

### Risks

- Redis가 단일 장애점이 된다. Redis 장애 시 전 인스턴스에서 로그인이 불가능해진다.
- 세션 직렬화 형식과 TTL 정책을 새로 정해야 하며, 정하지 않으면 만료 동작이 기존과 달라질 수 있다.
- 전환 시점에 기존 인메모리 세션은 모두 무효화되므로 사용자 재로그인이 발생한다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반 구현으로 교체 (직렬화 형식, 키 접두사, TTL 결정 포함)
- [ ] Redis 접속 설정(호스트/포트/자격 증명)을 환경 변수로 분리
- [ ] 인스턴스 간 세션 공유 및 인스턴스 재시작 후 세션 유지 테스트
- [ ] Redis 가용성·연결 실패·응답 지연 모니터링 추가
- [ ] 배포 환경에 Redis 프로비저닝 및 설정 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 모듈 전역 dict 구현으로 되돌리고 `requirements.txt`에서 `redis==5.0.8`을 제거한다. 단 롤백하면 3대 구성에서 로그인이 풀리는 문제가 다시 발생한다.
- **Migration Cost:** Low
