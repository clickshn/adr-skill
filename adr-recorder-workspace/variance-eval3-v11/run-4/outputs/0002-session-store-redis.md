# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 프로세스 내 dict에서 Redis로 옮겨 인스턴스 간에 공유한다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

세션은 현재 `app/session.py`의 프로세스 내 dict(`_sessions`)에 저장된다. 세션이 프로세스에 갇혀 있어
인스턴스 간에 공유되지 않는다. 애플리케이션 서버를 3대로 늘리면서, 로그인한 사용자의 요청이 세션을
만든 인스턴스가 아닌 다른 인스턴스로 라우팅되면 세션을 찾지 못해 로그인이 풀리는 문제가 발생했다.

### Constraints

- 서버 3대 수평 확장 구성을 유지해야 한다.
- 기존 스택은 FastAPI + uvicorn + SQLAlchemy이며, `requirements.txt`에 `redis==5.0.8`이 이미 추가되어
  있다(아직 커밋되지 않은 워킹 트리 변경).

## Decision

### Selected

- **Technology:** Redis (클라이언트: redis-py 5.0.8)
- **Architecture:** 세션을 애플리케이션 프로세스 외부의 공유 저장소에 두어, 3대의 서버가 동일한 세션
  상태를 읽고 쓰도록 한다.
- **Implementation:** `app/session.py`의 `get`/`put`을 dict 접근에서 Redis 키 접근으로 교체한다.
  모듈 인터페이스(`get(session_id)`, `put(session_id, data)`)는 그대로 유지해 호출부 변경을 최소화한다.

## Rationale

1. 로그인이 풀리는 원인이 세션이 프로세스에 묶여 있다는 점이므로, 세션을 프로세스 밖 공유 저장소로
   옮기면 요청이 어느 인스턴스로 가든 동일한 세션을 조회할 수 있다.
2. 세션은 세션 ID로 값을 읽고 쓰는 키-값 접근 패턴이라 Redis의 기본 자료구조에 그대로 대응된다.
3. 세션 수명이 프로세스 수명과 분리되어, 재배포·프로세스 재시작으로 로그인이 끊기지 않는다.

## Alternatives

### 프로세스 메모리 유지 (현행)

- **Pros:** 추가 인프라와 의존성이 없고, 구현이 이미 존재한다.
- **Cons:** 세션이 인스턴스별로 분리되어 수평 확장과 양립하지 않는다.
- **Rejected because:** 서버를 3대로 늘리자 로그인이 풀리는 문제가 실제로 발생했다.

## Consequences

### Positive

- 요청이 어느 인스턴스로 라우팅되어도 세션이 유지되어 로그인 풀림이 해소된다.
- 서버 대수를 더 늘릴 때 세션 저장소가 제약이 되지 않는다.
- 재배포·프로세스 재시작 후에도 로그인 상태가 유지된다.

### Negative

- Redis라는 운영 구성 요소가 새로 생긴다(프로비저닝, 모니터링, 장애 대응).
- 세션 조회마다 네트워크 왕복이 추가된다.
- dict를 그대로 보관하던 것과 달리 세션 데이터의 직렬화 형식을 정해야 한다.

### Risks

- Redis가 단일 장애점이 되면 전체 로그인 기능이 중단된다.
- 키 네임스페이스·TTL·직렬화 형식을 확정하지 않고 배포하면 세션 해석이 어긋날 수 있다.
- 전환 배포 시점에 메모리에 있던 기존 세션은 모두 유실되어 사용자 재로그인이 필요하다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체 (키 네임스페이스·TTL·직렬화 형식 확정)
- [ ] 인스턴스 3대 환경에서 로그인 유지 및 로그아웃 동작 테스트
- [ ] Redis 가용성·지연·메모리 사용량 모니터링 추가
- [ ] Redis 접속 설정(환경변수)과 배포 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 83bb4e5에 담긴 프로세스 메모리 dict 구현으로 되돌리고
  `requirements.txt`에서 `redis==5.0.8`을 제거한다. 되돌리면 다중 인스턴스 로그인 풀림 문제도 함께
  돌아온다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py` (현행 프로세스 메모리 구현, 커밋 83bb4e5), `requirements.txt`
  (`redis==5.0.8` 추가, 미커밋 워킹 트리 변경)
