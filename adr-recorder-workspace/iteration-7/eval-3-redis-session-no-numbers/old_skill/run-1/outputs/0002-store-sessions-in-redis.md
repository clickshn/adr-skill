# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 로그인 세션 저장소를 각 서버의 프로세스 메모리(dict)에서 공유 Redis로 옮긴다.
- **Scope:** member-portal / 세션 저장소 (app/session.py)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장되어, 세션을 만든 서버 프로세스 안에만 존재한다.
서버를 3대로 늘리면 로그인 요청을 처리한 서버와 이후 요청을 받는 서버가 달라질 수 있고, 이때 세션을 찾지 못해 로그인이 풀린다.

### Constraints

- 서버 3대가 같은 세션 데이터를 조회할 수 있어야 한다.
- 현재 세션 인터페이스는 `get(session_id)` / `put(session_id, data)` 두 함수뿐이며, 호출부는 이 인터페이스에만 의존한다.
- 현재 구현에는 세션 만료(TTL)나 삭제 로직이 없다.
- 스택: FastAPI 0.112.2, uvicorn 0.30.6, SQLAlchemy 2.0.32.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 모든 서버 인스턴스가 하나의 Redis를 공유 세션 저장소로 사용하고, 애플리케이션 서버는 세션 상태를 갖지 않는다.
- **Implementation:** `app/session.py`의 `get`/`put`을 인터페이스 그대로 유지한 채 내부 저장소를 dict에서 Redis 호출로 교체한다.

## Rationale

1. 세션이 프로세스 밖 공유 저장소에 있으면 어느 서버가 요청을 받아도 같은 세션을 조회할 수 있어, 서버 3대 증설 시 로그인이 풀리는 문제가 해소된다.
2. 세션 모듈이 `get`/`put` 두 함수로 캡슐화되어 있어 호출부 변경 없이 저장소만 교체할 수 있다.

## Consequences

### Positive

- 서버 대수와 무관하게 로그인 상태가 유지된다.
- 애플리케이션 서버가 무상태가 되어 서버 재시작·배포 시에도 세션이 사라지지 않는다.

### Negative

- Redis라는 운영 대상 인프라가 하나 추가된다.
- 세션 조회마다 네트워크 왕복이 생기고, 세션 데이터(dict)를 직렬화/역직렬화해야 한다.

### Risks

- Redis 장애 시 전체 서버에서 로그인·세션 조회가 불가능해진다(단일 장애점).
- 현재 구현에 TTL이 없으므로 그대로 옮기면 Redis에 세션이 무기한 쌓인다. 만료 정책을 함께 정해야 한다.
- 전환 시점에 각 서버 메모리에 있던 기존 세션은 이관되지 않아 사용자가 한 번 재로그인해야 한다.

## Implementation

- [x] `requirements.txt`에 `redis==5.0.8` 추가
- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체 (연결 설정은 환경 변수로 주입)
- [ ] 세션 TTL(만료) 정책 결정 및 적용
- [ ] 테스트: 서로 다른 인스턴스에서 같은 세션 ID 조회 시 로그인 상태가 유지되는지 검증
- [ ] 모니터링: Redis 가용성·연결 오류 알림
- [ ] 문서/설정 업데이트: Redis 접속 정보 등 배포 설정 추가

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 dict 기반 구현으로 되돌리고 `requirements.txt`에서 `redis`를 제거한다. 단, 서버가 여러 대인 상태에서 되돌리면 로그인이 풀리는 원래 문제가 재발한다.
- **Migration Cost:** Low

## References

- **Documentation:** 세션 모듈 `app/session.py`, 의존성 변경 `requirements.txt`(미커밋), 관련 커밋 `919a937` (feat: 로그인/로그아웃 API)
