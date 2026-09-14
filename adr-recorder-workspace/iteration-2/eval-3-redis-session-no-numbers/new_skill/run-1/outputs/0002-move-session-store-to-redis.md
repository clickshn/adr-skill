# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 로그인 세션을 각 서버 프로세스 메모리 대신 공유 Redis에 저장한다.
- **Scope:** member-portal / 세션 저장소 (`app/session.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장되어, 세션을 만든 서버 프로세스 안에만 존재한다. 서버를 3대로 늘리자 로그인한 서버와 다른 서버로 요청이 가면 세션을 찾지 못해 로그인이 풀리는 문제가 발생했다.

### Constraints

- 애플리케이션 서버 3대가 같은 세션을 조회할 수 있어야 한다.
- 기존 세션 모듈 인터페이스(`get(session_id)`, `put(session_id, data)`)를 호출하는 로그인/로그아웃 API(커밋 a7a3c11)가 이미 있다.
- Python 클라이언트는 `redis==5.0.8`로 `requirements.txt`에 추가되어 있다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 세션 상태를 애플리케이션 서버 밖의 공유 Redis로 옮겨, 각 서버는 세션을 로컬에 들고 있지 않는(stateless) 구조로 바꾼다.
- **Implementation:** `app/session.py`의 `get`/`put` 시그니처는 유지하고, 내부 `_sessions` dict를 Redis 읽기/쓰기로 교체한다. 세션 데이터(`dict`)는 Redis에 저장할 수 있도록 직렬화한다.

## Rationale

1. 프로세스 메모리 세션은 서버끼리 공유되지 않으므로, 서버 수가 늘어나는 한 로그인 풀림은 구조적으로 반복된다. 세션을 외부 공유 저장소로 옮기면 어느 서버로 요청이 가도 같은 세션을 조회할 수 있다.
2. 현재 세션 접근은 `get`/`put` 두 함수로 캡슐화된 키-값 조회라 Redis의 키-값 모델에 그대로 대응되고, 변경 범위를 `app/session.py` 한 파일로 한정할 수 있다.

## Consequences

### Positive

- 서버 3대 중 어느 서버로 요청이 가도 로그인이 유지된다.
- 세션이 서버 프로세스 밖에 있으므로 앱 재시작·배포 때 세션이 사라지지 않는다.
- 이후 서버를 더 늘려도 세션 저장소를 다시 바꿀 필요가 없다.

### Negative

- 운영할 인프라 구성요소(Redis)가 하나 늘어난다.
- 세션 조회마다 인메모리 dict 접근이 아니라 네트워크 왕복이 생긴다.
- 세션 데이터를 저장·조회할 때마다 직렬화·역직렬화가 필요하다.

### Risks

- Redis가 단일 장애점이 된다. Redis가 멈추면 세 서버 모두에서 세션 조회와 로그인이 실패한다.
- Redis 영속성 설정에 따라 Redis가 재시작되면 세션이 유실될 수 있다.
- 전환 시점에 각 서버 메모리에 있던 기존 세션은 옮겨지지 않으므로, 배포 직후 로그인 사용자가 한 번 로그아웃된다.
- Redis 네트워크 접근 제어·인증이 약하면 세션 탈취 경로가 된다.

## Implementation

- [ ] `app/session.py`의 `_sessions` dict를 Redis 클라이언트 기반 `get`/`put`으로 교체 (세션 만료 TTL 포함)
- [ ] 테스트: 서로 다른 서버 인스턴스에서 같은 세션 조회, Redis 연결 실패 시 동작 확인
- [ ] 모니터링: Redis 가용성·연결 오류, 세션 조회 지연
- [ ] 문서/설정 업데이트: Redis 접속 정보(호스트·인증)를 환경 설정으로 분리, 배포 문서 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 dict 구현으로 되돌리고 `requirements.txt`에서 `redis`를 제거한다. 인터페이스가 그대로라 코드 복구는 간단하지만, 서버가 여러 대인 상태로 되돌리면 로그인 풀림이 다시 생기므로 서버를 1대로 줄이거나 다른 공유 방식이 함께 필요하다.
- **Migration Cost:** Low

## References

- **Documentation:** `requirements.txt` (`redis==5.0.8` 추가, 미커밋), `app/session.py` (현재 프로세스 메모리 구현)
