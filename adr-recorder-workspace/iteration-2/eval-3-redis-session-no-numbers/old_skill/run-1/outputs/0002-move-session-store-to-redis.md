# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 세션 저장소를 애플리케이션 프로세스 메모리(dict)에서 Redis로 옮겨 모든 서버 인스턴스가 공유하도록 한다.
- **Scope:** member-portal / 세션 저장소 (`app/session.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장되어 각 서버 프로세스 메모리 안에만 존재한다. 서버를 3대로 늘리자 로그인한 인스턴스가 아닌 다른 인스턴스로 요청이 가면 세션을 찾지 못해 로그인이 풀리는 문제가 발생했다.

### Constraints

- 서버 3대로 수평 확장한 상태에서 어느 인스턴스가 요청을 받아도 같은 세션을 조회할 수 있어야 한다.
- 기존 스택: FastAPI 0.112.2 / uvicorn 0.30.6 / SQLAlchemy 2.0.32 (Python).

## Decision

### Selected

- **Technology:** Redis, Python 클라이언트 `redis==5.0.8` (requirements.txt에 추가됨)
- **Architecture:** 세션 상태를 애플리케이션 프로세스 밖의 공유 Redis 저장소로 옮기고, 앱 서버 3대가 이 저장소를 함께 쓴다(앱 서버에는 세션 상태를 두지 않음).
- **Implementation:** `app/session.py`의 `get`/`put`이 쓰는 저장소를 `_sessions` dict에서 Redis로 교체한다.

## Rationale

1. 세션을 공유 저장소에 두면 요청이 어느 인스턴스로 라우팅되더라도 같은 세션을 조회할 수 있어 로그인이 풀리는 문제가 해결된다.
2. 앱 서버에 세션 상태가 남지 않으므로 서버 대수가 바뀌어도 세션에는 영향이 없다.

## Consequences

### Positive

- 멀티 인스턴스 환경에서 로그인 상태가 유지된다.
- 앱 서버를 재시작하거나 배포해도 세션이 사라지지 않는다(현재는 프로세스 메모리에 있어 재시작하면 모두 사라진다).
- 서버를 더 늘릴 때 세션 때문에 걸리는 제약이 없어진다.

### Negative

- 운영해야 할 인프라 컴포넌트(Redis)가 하나 늘어난다.
- 세션을 읽고 쓸 때마다 Redis까지 네트워크 왕복이 생긴다.
- 세션 데이터(dict)를 직렬화·역직렬화해야 한다.

### Risks

- Redis에 장애가 나면 모든 인스턴스의 로그인·세션 조회가 함께 실패한다(단일 장애점).
- 지금 구현에는 세션 만료·삭제 로직이 없다(`get`/`put`만 있음). Redis로 옮기면서 TTL을 정하지 않으면 세션 키가 계속 쌓인다.

## Implementation

- [ ] 구현 작업: `app/session.py`의 `get`/`put`을 Redis 클라이언트 기반으로 교체(직렬화 포함), 세션 TTL 적용
- [ ] 테스트: 3대 구성에서 요청이 다른 인스턴스로 가도 로그인이 유지되는지 확인
- [ ] 모니터링: Redis 가용성, 메모리 사용량, 연결 오류
- [ ] 문서/설정 업데이트: Redis 접속 정보(호스트·인증)를 환경 설정으로 분리, `requirements.txt` 변경 커밋

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 메모리 dict 구현으로 되돌리고 `redis` 의존성을 제거한다. 롤백하면 Redis에 있던 세션은 사라지고(재로그인 필요) 멀티 인스턴스 환경에서 원래 문제가 다시 생긴다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py`(현재 메모리 기반 세션 구현), `requirements.txt`(`redis==5.0.8` 추가, 미커밋), 관련 커밋 `a7a3c11`(로그인/로그아웃 API)
