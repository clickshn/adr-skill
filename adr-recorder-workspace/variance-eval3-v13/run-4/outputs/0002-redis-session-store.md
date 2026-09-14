# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 프로세스 메모리 dict에서 Redis로 옮긴다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

- 현재 세션은 `app/session.py`의 프로세스 메모리 dict(`_sessions`)에 보관되며, 서버 프로세스마다 별도의 사본이 존재한다.
- 서버를 3대로 늘리면서, 로그인한 사용자의 다음 요청이 다른 서버로 라우팅되면 해당 서버에 세션이 없어 로그인이 풀리는 문제가 발생했다.

### Constraints

- 기존 스택은 FastAPI + uvicorn + SQLAlchemy이며, 세션 접근은 `app/session.py`의 `get`/`put` 두 함수로 캡슐화되어 있다.
- `requirements.txt`에 `redis==5.0.8`이 이미 추가되어 있다(아직 커밋되지 않은 작업 트리 변경).

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 세션을 애플리케이션 프로세스 외부의 공유 저장소에 두어, 3대의 서버가 같은 세션을 조회하도록 한다.
- **Implementation:** `app/session.py`의 `get`/`put`을 Redis 키-값 접근으로 교체한다. 호출부가 쓰는 함수 인터페이스는 그대로 유지한다.

## Rationale

1. 세션이 프로세스 밖 공유 저장소에 있으면 요청이 어느 서버로 가든 같은 세션을 조회할 수 있어, 서버 증설로 생긴 로그인 풀림의 원인이 직접 제거된다.
2. 세션 접근 경로가 `get`/`put` 두 함수로 이미 캡슐화되어 있어 저장소 교체로 바뀌는 코드 범위가 작다.
3. 세션은 만료 시간을 갖는 휘발성 키-값 데이터라 Redis의 저장 모델과 맞는다.

## Alternatives

### 프로세스 메모리 dict 유지(현행)

- **Pros:** 외부 의존성이 없고 조회 지연이 사실상 없다.
- **Cons:** 세션이 개별 프로세스에 갇혀 서버 간 공유가 불가능하다.
- **Rejected because:** 서버를 3대로 늘리자 요청이 다른 서버로 라우팅될 때 세션을 찾지 못해 로그인이 풀렸다.

## Consequences

### Positive

- 서버 대수와 무관하게 세션이 유지되어, 수평 확장 시 로그인이 풀리는 문제가 해소된다.
- 배포·재시작으로 프로세스가 내려가도 세션이 사라지지 않는다.

### Negative

- Redis라는 운영 컴포넌트가 하나 늘어난다(설치·접속 설정·모니터링·백업 판단 필요).
- 세션 조회마다 네트워크 왕복이 생겨 메모리 조회보다 지연이 늘어난다.
- 세션 값을 dict 그대로 담을 수 없어 직렬화 포맷을 정해야 한다.

### Risks

- Redis가 단일 장애점이 되면 3대 서버 전체에서 로그인이 불가능해진다.
- 세션 TTL·키 네이밍 정책이 아직 정해지지 않아, 정하지 않고 옮기면 세션이 무한정 쌓이거나 예상보다 일찍 만료될 수 있다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반 구현으로 교체(직렬화 포맷·키 접두사·TTL 포함)
- [ ] 서버 3대 구성에서 로그인 후 다른 서버로 라우팅될 때 세션이 유지되는지 테스트
- [ ] Redis 가용성·응답 지연·메모리 사용량 모니터링 추가
- [ ] Redis 접속 정보(호스트/포트/DB/TTL)를 배포 설정에 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 프로세스 메모리 dict 구현으로 되돌리고 `requirements.txt`에서 `redis==5.0.8`을 제거한다. 되돌리기 기준점은 현재 HEAD(ba84cb2)다. 단, 되돌리면 서버 3대 구성에서 로그인 풀림 문제가 그대로 재현된다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py` — 프로세스 메모리 세션 구현(69b2c22에서 추가), `requirements.txt` — `redis==5.0.8` 추가(작업 트리 미커밋 변경)
