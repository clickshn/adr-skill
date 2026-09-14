# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 데이터를 프로세스 메모리 dict 대신 Redis에 저장한다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

애플리케이션 서버를 3대로 늘린 뒤 로그인이 유지되지 않고 풀리는 문제가 발생했다.
현재 세션은 `app/session.py`의 프로세스 내 딕셔너리(`_sessions`)에 보관되어 있어 인스턴스마다
서로 다른 세션 사본을 갖는다. 요청이 로그인 시점과 다른 인스턴스로 분배되면 해당 세션을 찾지
못해 로그아웃된 것처럼 동작한다. 프로세스가 재시작되면 세션이 전부 사라지는 문제도 같은 원인이다.

### Constraints

- FastAPI + uvicorn 기반이며, 서버 3대 구성을 유지한다.
- 세션 저장소 인터페이스는 `get(session_id)` / `put(session_id, data)` 두 함수로 고정되어 있어
  호출부 변경 없이 구현만 교체할 수 있다.
- `requirements.txt`에 `redis==5.0.8`이 이미 추가되어 있다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 모든 애플리케이션 인스턴스가 공유하는 외부 세션 저장소를 두고, 세션 조회·저장을
  그 저장소로 일원화한다. 애플리케이션 인스턴스는 세션 상태를 갖지 않는다(stateless).
- **Implementation:** `app/session.py`의 `_sessions` 딕셔너리를 Redis 클라이언트 호출로 교체한다.
  `get`/`put` 시그니처는 그대로 두고 내부에서 직렬화/역직렬화와 만료(TTL) 처리를 담당한다.

## Rationale

1. 로그인이 풀리는 직접 원인은 세션이 프로세스 로컬 메모리에 있어 인스턴스 간에 공유되지 않는
   것이므로, 인스턴스 바깥의 공유 저장소로 옮기면 문제가 해소된다.
2. 세션 저장소가 외부로 분리되면 인스턴스 증설·재배포·프로세스 재시작이 로그인 상태에 영향을
   주지 않는다.
3. 저장소 접근이 `get`/`put` 두 함수로 캡슐화되어 있어 호출부를 건드리지 않고 교체할 수 있다.

## Consequences

### Positive

- 어느 인스턴스로 요청이 분배되어도 동일한 세션을 조회할 수 있어 로그인 풀림이 해소된다.
- 서버 재시작·재배포 시에도 세션이 유지된다.
- 인스턴스가 세션 상태를 갖지 않으므로 이후 증설이 자유롭다.

### Negative

- Redis라는 운영 구성 요소가 하나 늘어난다(설치·모니터링·백업·접속 정보 관리).
- 세션 조회마다 네트워크 왕복이 추가되고, dict에 직접 담던 값을 직렬화해야 한다.

### Risks

- Redis 장애 시 전 인스턴스의 로그인이 동시에 불가능해진다(단일 장애점).
- 메모리 dict에는 없던 만료 정책이 필요하다. TTL을 정하지 않으면 세션 키가 무한히 쌓인다.
- 전환 배포 시점에 기존 메모리 세션은 모두 무효화되어 사용자 재로그인이 발생한다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반 구현으로 교체 (직렬화, TTL 포함)
- [ ] 인스턴스 3대에서 교차 요청 시 세션이 유지되는지 테스트, 프로세스 재시작 후 세션 유지 테스트
- [ ] Redis 연결 실패율·응답 지연·키 개수 모니터링
- [ ] Redis 접속 설정(호스트/포트/인증) 환경변수화 및 배포 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 기존 딕셔너리 구현으로 되돌리고 `requirements.txt`에서
  `redis==5.0.8`을 제거한다. 되돌리기 직전 기준점은 커밋 `ba84cb2`다. 단, 롤백하면 3대 구성에서
  로그인이 풀리는 원래 문제가 그대로 재발한다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py`, `requirements.txt`
