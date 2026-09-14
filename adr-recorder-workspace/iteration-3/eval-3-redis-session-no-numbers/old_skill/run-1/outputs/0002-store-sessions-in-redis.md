# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 세션 저장소를 프로세스 메모리(dict)에서 Redis로 옮겨 여러 서버 인스턴스가 세션을 공유하게 한다.
- **Scope:** member-portal / 세션 저장소 (`app/session.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장되어 각 서버 프로세스 메모리에만 존재한다. 서버를 3대로 늘리자, 로그인을 처리한 서버가 아닌 다른 서버로 요청이 가면 세션을 찾지 못해 로그인이 풀리는 문제가 발생했다.

### Constraints

- 서버 3대가 동일한 세션 데이터를 조회·갱신할 수 있어야 한다.
- 기존 세션 모듈의 인터페이스(`get(session_id)`, `put(session_id, data)`)를 호출하는 로그인/로그아웃 API(커밋 e776c53)가 이미 존재한다.
- 의존성은 `redis==5.0.8`로 고정해 `requirements.txt`에 추가했다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 세션 상태를 애플리케이션 프로세스 밖의 공유 저장소(Redis)에 두고, 모든 서버 인스턴스가 이를 조회하는 무상태(stateless) 앱 서버 구조로 전환한다.
- **Implementation:** `app/session.py`의 `get`/`put` 인터페이스는 유지하고, 내부 저장소를 dict에서 Redis 클라이언트 호출로 교체한다.

## Rationale

1. 세션을 프로세스 밖 공유 저장소에 두면 요청이 어느 서버로 라우팅되든 같은 세션을 조회할 수 있어, 다중 서버 환경에서 로그인이 풀리는 문제를 직접 해소한다.
2. 앱 서버가 세션 상태를 갖지 않게 되어 이후 서버 대수를 늘리거나 줄이는 데 세션이 제약이 되지 않는다.
3. 세션 모듈이 `get`/`put` 두 함수로 캡슐화되어 있어, 호출부 변경 없이 저장소만 교체할 수 있다.

## Consequences

### Positive

- 서버 3대 간 세션이 공유되어 서버 간 요청 이동 시 로그인 유지.
- 앱 프로세스 재시작·배포 시에도 세션이 프로세스와 함께 사라지지 않음.

### Negative

- 운영해야 할 인프라 컴포넌트(Redis)가 하나 늘어난다.
- 세션 조회마다 네트워크 왕복이 추가된다.
- dict 객체를 그대로 저장하던 방식에서 직렬화/역직렬화가 필요해진다.

### Risks

- Redis 장애 시 모든 서버의 로그인/세션 조회가 동시에 실패할 수 있다(단일 장애점).
- 세션 만료(TTL)를 두지 않으면 Redis에 세션이 무한히 누적될 수 있다.
- 세션 데이터가 네트워크를 거치므로 Redis 접근 제어(인증, 네트워크 격리)가 필요하다.

## Implementation

- [ ] `app/session.py`의 `_sessions` dict를 Redis 클라이언트 기반 `get`/`put`으로 교체 (직렬화 포함)
- [ ] 세션 만료(TTL) 정책 적용
- [ ] 다중 인스턴스 환경에서 로그인 유지 여부 테스트
- [ ] Redis 연결 상태·오류 모니터링
- [ ] Redis 접속 정보 설정 추가 및 배포 문서 업데이트

## Reversibility

- **Reversible:** Partial
- **Rollback:** `app/session.py`를 인메모리 dict 구현으로 되돌리고 `redis` 의존성을 제거한다. 단, 롤백 시 Redis에 저장된 세션은 이전되지 않아 사용자 재로그인이 필요하며, 다중 서버에서 로그인이 풀리는 원래 문제가 다시 발생한다.
- **Migration Cost:** Low

## References

- **Documentation:** `requirements.txt` (`redis==5.0.8` 추가, 미커밋), `app/session.py` (현재 인메모리 구현), 관련 커밋 e776c53 (로그인/로그아웃 API)
