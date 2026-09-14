# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 앱 프로세스 메모리에서 외부 Redis로 옮겨 서버 간에 공유한다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

세션은 현재 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장된다. 즉 세션이 각 앱 프로세스의 메모리 안에만 존재한다. 앱 서버를 3대로 늘리면서, 로그인한 사용자의 후속 요청이 다른 서버로 라우팅되면 그 서버에는 세션이 없어 로그인이 풀리는 문제가 발생했다.

### Constraints

- 앱 서버 3대가 동일한 세션을 공유해야 한다.
- 기존 `app/session.py`의 `get(session_id)` / `put(session_id, data)` 인터페이스를 쓰는 호출부가 있다(로그인/로그아웃 API).
- 스택은 FastAPI + uvicorn + SQLAlchemy이며, `redis==5.0.8`이 이미 requirements.txt에 추가되어 있다.

## Decision

### Selected

- **Technology:** redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 세션을 앱 프로세스 외부의 공유 Redis에 저장한다. 앱 서버는 세션에 대해 무상태가 되고, 어느 인스턴스가 요청을 받아도 같은 세션을 읽는다.
- **Implementation:** `app/session.py`의 `get`/`put` 구현만 Redis 클라이언트 기반으로 교체하고, 호출부 시그니처는 유지한다.

## Rationale

1. 프로세스 메모리 저장소는 구조상 인스턴스 간 공유가 불가능하므로, 서버를 3대로 늘린 상태에서 로그인 풀림을 해결할 수 없다.
2. 세션 접근이 `app/session.py`의 `get`/`put` 두 함수로 격리돼 있어, 그 뒤의 저장소만 교체하면 호출부 변경 없이 공유 저장소로 전환할 수 있다.
3. 세션은 키-값 조회 위주에 만료가 필요한 데이터라 Redis의 키-값 + TTL 모델에 그대로 맞는다.

## Alternatives

### 프로세스 메모리 세션 저장소 유지 (현행)

- **Pros:** 외부 컴포넌트가 없어 구성이 단순하고, 네트워크 왕복이 없다.
- **Cons:** 인스턴스 간 세션 공유가 불가능하고, 프로세스 재시작 시 세션이 모두 사라진다.
- **Rejected because:** 서버를 3대로 늘리자 요청이 다른 서버로 갈 때 로그인이 풀리는 문제가 실제로 발생했다.

## Consequences

### Positive

- 요청이 어느 서버로 라우팅되든 동일한 세션을 조회할 수 있어 로그인 풀림이 해소된다.
- 앱 서버가 세션에 대해 무상태가 되어 인스턴스 증설·재배포 중에도 세션이 유지된다.

### Negative

- 운영해야 할 인프라 구성요소(Redis)가 하나 늘어난다.
- 세션 조회마다 네트워크 왕복이 추가된다.

### Risks

- Redis가 단일 장애점이 된다. 장애 시 전체 사용자의 인증이 영향을 받는다.
- 세션 값의 직렬화 포맷과 TTL(만료) 정책이 아직 정해지지 않았다. 현재 메모리 구현에는 만료 개념이 없다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 클라이언트 기반으로 교체 (직렬화 포맷, 키 프리픽스, TTL 결정 포함)
- [ ] 서버 2대 이상 환경에서 로그인 후 다른 인스턴스로 요청이 가도 세션이 유지되는지 테스트
- [ ] Redis 연결 실패/타임아웃 및 가용성 모니터링
- [ ] Redis 접속 정보 설정(환경변수) 및 배포 구성 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** requirements.txt에서 `redis==5.0.8`을 제거하고 `app/session.py`를 프로세스 메모리 dict 구현(69b2c22에서 도입된 형태)으로 되돌린다. 되돌리는 시점의 활성 세션은 소실되어 사용자는 재로그인해야 하고, 서버 3대 환경에서는 로그인 풀림 문제가 다시 나타난다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py` (현행 프로세스 메모리 구현, 69b2c22에서 도입), requirements.txt의 `redis==5.0.8` 추가(미커밋 변경)
