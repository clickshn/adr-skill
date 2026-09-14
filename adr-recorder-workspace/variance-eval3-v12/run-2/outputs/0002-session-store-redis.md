# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 프로세스 메모리 딕셔너리에서 Redis로 옮긴다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

세션이 각 애플리케이션 프로세스의 메모리(`app/session.py`의 모듈 전역 `_sessions` 딕셔너리)에만
저장된다. 서버를 3대로 늘리면서 요청이 로그인 때와 다른 서버로 분배되면 해당 프로세스에는 세션이
없어 로그인이 풀리는 문제가 발생했다.

### Constraints

- 서버 대수를 3대로 유지해야 하므로 단일 프로세스 전제를 되돌릴 수 없다.
- 현재 스택은 FastAPI + uvicorn + SQLAlchemy이며, 세션 접근은 `get`/`put` 두 함수로만 이뤄져
  저장소 교체 범위가 이 모듈에 한정된다.

## Decision

### Selected

- **Technology:** Redis (`redis==5.0.8`, requirements.txt에 추가됨)
- **Architecture:** 모든 애플리케이션 인스턴스가 공유하는 외부 세션 저장소를 둔다. 세션 상태를
  프로세스 밖으로 빼내 애플리케이션 서버를 무상태로 만든다.
- **Implementation:** `app/session.py`의 `get`/`put` 인터페이스를 유지한 채 내부 구현만 Redis
  클라이언트 호출로 교체한다. 호출 측 코드는 수정하지 않는다.

## Rationale

1. 세션을 프로세스 밖 공유 저장소에 두면 어느 서버로 요청이 가더라도 동일한 세션을 읽을 수 있어
   3대 확장 시 로그인이 풀리는 원인이 제거된다.
2. 세션 접근 지점이 `get`/`put` 두 함수뿐이라 저장소 교체 비용이 낮고 영향 범위가 좁다.
3. 세션은 만료되는 휘발성 데이터이므로 TTL을 기본 제공하는 Redis의 특성과 맞는다.

## Alternatives

### 프로세스 메모리 유지 (현행)

- **Pros:** 추가 인프라가 없고 의존성도 늘지 않으며 접근 지연이 가장 짧다.
- **Cons:** 세션이 프로세스에 묶여 수평 확장과 재배포 시 유실된다.
- **Rejected because:** 서버를 3대로 늘리면서 로그인이 풀리는 문제가 실제로 발생했다.

## Consequences

### Positive

- 애플리케이션 서버가 무상태가 되어 서버 증설·재배포 시에도 로그인이 유지된다.
- 인스턴스별 세션 편차가 사라져 장애 재현과 디버깅이 쉬워진다.

### Negative

- Redis라는 운영 대상 인프라와 런타임 의존성이 새로 늘어난다.
- 세션 조회마다 네트워크 왕복이 추가된다.

### Risks

- Redis가 단일 장애점이 된다. Redis 장애 시 전 서버의 로그인이 동시에 영향을 받는다.
- 세션 데이터 직렬화 방식과 TTL 정책을 새로 정해야 하며, 잘못 잡으면 조기 로그아웃이나 세션
  누적이 발생한다.
- Redis 접속 정보가 새로운 비밀 정보로 추가되어 환경별 설정 관리가 필요하다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 클라이언트 기반으로 교체 (인터페이스 유지)
- [ ] Redis 접속 설정(호스트/포트/비밀번호)을 환경변수로 분리
- [ ] 세션 TTL 및 직렬화 포맷 결정
- [ ] 다중 인스턴스 환경에서 로그인 유지 테스트 (서버 A 로그인 → 서버 B 요청)
- [ ] Redis 연결 실패·지연에 대한 모니터링/알람 추가
- [ ] 배포 환경에 Redis 인스턴스 provisioning 및 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 69b2c22 시점의 메모리 딕셔너리 구현으로 되돌리고
  requirements.txt에서 `redis==5.0.8`을 제거한다. 단, 되돌리면 3대 구성에서 로그인이 풀리는
  문제가 다시 발생하므로 서버 1대 구성으로 함께 되돌려야 한다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/session.py` (현행 메모리 구현, 69b2c22에서 추가), `requirements.txt`
  (`redis==5.0.8` 추가, 미커밋 변경)
