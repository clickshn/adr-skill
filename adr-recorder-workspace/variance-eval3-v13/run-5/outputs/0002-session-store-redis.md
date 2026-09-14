# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 각 프로세스의 인메모리 dict에서 공유 Redis로 옮긴다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

세션은 현재 애플리케이션 프로세스 메모리의 dict(`app/session.py`의 `_sessions`)에 보관된다.
서버를 3대로 늘리자 요청이 세션을 만든 인스턴스가 아닌 다른 인스턴스로 라우팅되면 세션을
찾지 못해 로그인이 풀리는 문제가 발생했다.

### Constraints

- FastAPI + uvicorn 기반의 다중 인스턴스(3대) 구성에서 동작해야 한다.
- 세션 데이터는 인스턴스 간에 공유되어야 한다.
- `requirements.txt`에 `redis==5.0.8`이 이미 추가되어 있다.

## Decision

### Selected

- **Technology:** Redis (redis-py 5.0.8)
- **Architecture:** 프로세스 내부 상태를 제거하고, 모든 인스턴스가 공유하는 외부 세션 스토어를 둔다.
- **Implementation:** `app/session.py`의 `get`/`put`을 dict 접근 대신 Redis 클라이언트 호출로 교체하고, 세션 키에 TTL을 부여한다.

## Rationale

1. 세션을 프로세스 밖으로 빼면 어느 인스턴스가 요청을 받아도 동일한 세션을 읽을 수 있어, 3대 확장 후 발생한 로그인 풀림의 원인이 제거된다.
2. 애플리케이션 인스턴스가 무상태가 되어 재배포·재시작·스케일 아웃 시 세션이 소실되지 않는다.
3. 현재 세션 접근 지점이 `get`/`put` 두 함수뿐이라, 저장소 교체 범위가 좁고 호출부 변경이 필요 없다.
4. Redis는 TTL 기반 만료를 자체 지원해 세션 수명 관리를 별도 구현하지 않아도 된다.

## Alternatives

### 프로세스 메모리(dict) 세션 저장소 유지

- **Pros:** 외부 인프라 의존이 없고, 구현이 단순하며 네트워크 왕복이 없다.
- **Cons:** 세션이 인스턴스에 묶여 공유되지 않고, 프로세스 재시작 시 소실된다.
- **Rejected because:** 서버를 3대로 늘린 뒤 다른 인스턴스로 라우팅된 요청에서 로그인이 풀리는 문제가 실제로 발생했다.

## Consequences

### Positive

- 인스턴스 수와 무관하게 로그인 세션이 유지된다.
- 애플리케이션 서버가 무상태가 되어 수평 확장과 무중단 재배포가 쉬워진다.

### Negative

- Redis라는 운영 구성 요소가 새로 늘어난다(배포·모니터링·백업 대상 추가).
- 세션 조회마다 네트워크 왕복이 추가된다.

### Risks

- Redis가 단일 장애점이 되어, 장애 시 전 인스턴스의 로그인이 동시에 영향을 받는다.
- Redis 접속 정보·네트워크 경로가 환경별로 설정되어야 하며, 누락 시 기동 실패로 이어진다.
- 세션 TTL 설정을 누락하면 만료되지 않은 세션 키가 계속 쌓인다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체하고 세션 TTL 적용
- [ ] Redis 접속 설정(호스트/포트/DB)을 환경 변수로 분리
- [ ] 다중 인스턴스 환경에서 로그인 유지 테스트
- [ ] Redis 가용성·연결 실패·메모리 사용량 모니터링 추가
- [ ] 배포 문서에 Redis 의존성 및 설정 항목 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 커밋 `ba84cb2` 시점의 인메모리 dict 구현으로 되돌리고 `requirements.txt`에서 `redis==5.0.8`을 제거한다. 다만 롤백 시 3대 구성에서 로그인 풀림 문제가 다시 발생하므로 인스턴스 수 축소가 동반되어야 한다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py` (현행 세션 저장소 구현), `requirements.txt` (redis==5.0.8 추가)
