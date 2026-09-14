# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 프로세스 메모리(dict)에서 Redis로 옮긴다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 프로세스 내 전역 dict(`_sessions`)에 저장된다(69b2c22에서 도입).
단일 서버에서는 동작하지만, 서버를 3대로 늘리면서 요청이 세션을 보유하지 않은 서버로
라우팅되면 로그인이 풀리는 문제가 발생하고 있다. 세션 상태가 각 프로세스에 갇혀 있어
서버 간에 공유되지 않는 것이 원인이다.

### Constraints

- 서버 3대 구성을 유지해야 한다(스케일아웃을 되돌리는 선택지는 고려 대상이 아니다).
- 기존 스택은 FastAPI + uvicorn + SQLAlchemy이며, 세션 접근 인터페이스는 `get`/`put` 두 개다.

## Decision

### Selected

- **Technology:** redis==5.0.8 (requirements.txt에 추가됨)
- **Architecture:** 세션 상태를 애플리케이션 프로세스 밖의 공유 저장소(Redis)로 분리해,
  3대의 서버가 동일한 세션을 조회·갱신하도록 한다.
- **Implementation:** `app/session.py`의 `get`/`put`을 Redis 클라이언트 기반으로 교체한다.
  호출부 인터페이스는 유지한다.

## Rationale

1. 로그인이 풀리는 직접 원인이 세션의 프로세스 지역성이므로, 저장소를 프로세스 밖 공유
   저장소로 옮기는 것이 원인을 제거하는 방법이다.
2. 세션은 키-값 조회·갱신과 만료가 전부인 접근 패턴이라 Redis의 모델과 맞고, 현재
   `get`/`put` 2개 함수만 교체하면 되어 변경 범위가 작다.

## Alternatives

### 현행 유지 (프로세스 메모리 dict)

- **Pros:** 추가 인프라·의존성이 없고, 이미 동작하는 코드다.
- **Cons:** 세션이 프로세스에 갇혀 서버 간 공유가 불가능하다.
- **Rejected because:** 서버를 3대로 늘리면서 로그인이 풀리는 문제가 실제로 발생했다.

## Consequences

### Positive

- 어느 서버로 라우팅되든 동일한 세션을 보므로 로그인 풀림 문제가 해소된다.
- 서버 재시작·배포 시 세션이 사라지지 않는다.
- 세션이 서버 대수와 분리되어 이후 스케일아웃에 제약이 없다.

### Negative

- Redis라는 운영 구성요소와 의존성이 새로 추가된다.
- 세션 조회가 인프로세스 메모리 접근에서 네트워크 왕복으로 바뀐다.

### Risks

- Redis가 단일 장애점이 된다. 장애 시 전체 로그인이 영향을 받는다.
- 전환 시점의 기존 인메모리 세션은 승계되지 않아 사용자가 재로그인해야 한다.
- 세션 만료(TTL) 정책을 Redis 쪽에 명시적으로 설정하지 않으면 세션이 무기한 남을 수 있다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체 (TTL 설정 포함)
- [ ] 서버 3대에서 교차 요청 시 세션이 유지되는지 테스트
- [ ] Redis 연결 실패·지연 모니터링
- [ ] Redis 접속 정보 설정화 및 배포 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 69b2c22의 dict 구현으로 되돌리고 requirements.txt에서
  redis==5.0.8을 제거한다. 단, 되돌리면 3대 구성에서 로그인 풀림 문제가 재발한다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py` (현행 인메모리 구현, 69b2c22), `requirements.txt`
  (redis==5.0.8 추가, 아직 미커밋)
