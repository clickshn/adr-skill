# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 세션 저장소를 애플리케이션 프로세스 메모리에서 Redis로 옮겨 인스턴스 간에 공유한다.
- **Scope:** member-portal
- **Decision Source:** Human

---

## Context

### Problem

세션을 애플리케이션 프로세스 메모리(`app/session.py`의 모듈 전역 dict `_sessions`)에 보관해 왔다. 서버를 3대로 늘리면서 같은 사용자의 요청이 로그인 때와 다른 인스턴스로 라우팅되면 그 인스턴스에는 세션이 없어 로그인이 풀리는 문제가 발생했다.

### Constraints

- 서버 3대 수평 확장 구성을 유지한 채로 해결해야 한다.
- 세션 접근 지점은 `app/session.py`의 `get`/`put` 두 함수로, 호출부 인터페이스는 유지하는 것이 바람직하다.
- 현재 스택은 FastAPI 0.112.2 + uvicorn 0.30.6 + SQLAlchemy 2.0.32이며, `requirements.txt`에 `redis==5.0.8`이 이미 추가되어 있다.

## Decision

### Selected

- **Technology:** Redis (Python 클라이언트 `redis==5.0.8`)
- **Architecture:** 프로세스 내부 dict 기반 세션 저장 → 3대 인스턴스가 공유하는 외부 세션 저장소. 애플리케이션 인스턴스는 세션 상태를 보유하지 않는다.
- **Implementation:** `app/session.py`의 `get`/`put` 구현만 Redis 클라이언트 호출로 교체하고 함수 시그니처는 유지한다.

## Rationale

1. 세션을 프로세스 밖 공유 저장소로 분리하면 요청이 어느 인스턴스로 라우팅되어도 같은 세션을 읽으므로, 3대 확장으로 드러난 로그인 풀림의 원인이 직접 제거된다.
2. 교체 지점이 `app/session.py`의 `get`/`put` 두 함수로 한정되어 있어 호출부 변경 없이 저장소만 바꿀 수 있다.

## Alternatives

### 현행 유지 (프로세스 메모리 세션)

- **Pros:** 외부 의존성과 운영 컴포넌트가 없고, 세션 조회가 프로세스 내부 dict 접근이라 가장 빠르다.
- **Cons:** 인스턴스 간 세션 공유가 불가능하고, 재배포·재시작 시 세션이 전량 유실된다.
- **Rejected because:** 서버를 3대로 늘린 뒤 로그인이 풀리는 문제가 실제로 발생했다.

## Consequences

### Positive

- 인스턴스 수와 무관하게 세션이 유지되어 로그인 풀림 문제가 해소된다.
- 애플리케이션 인스턴스가 무상태가 되어 증설·재배포 시 세션을 신경 쓰지 않아도 된다.

### Negative

- Redis라는 운영 컴포넌트가 새로 추가된다(배포·모니터링·용량 관리 대상 증가).
- 세션 조회·저장마다 네트워크 왕복이 발생한다.

### Risks

- Redis 장애 시 전 인스턴스에서 로그인이 불가능해진다(단일 장애점). 가용성 구성이 필요하다.
- 전환 시점에 메모리에 남아 있던 기존 세션은 유실되어 사용자 전원이 재로그인하게 된다.
- 세션 데이터가 프로세스 밖으로 나가므로 Redis 접근 제어와 전송 구간 보호를 확인해야 한다.

## Implementation

- [ ] `app/session.py`의 `get`/`put`을 Redis 기반으로 교체(키 네임스페이스, 직렬화 방식, TTL 정의)
- [ ] 3대 인스턴스 환경에서 로그인 후 다른 인스턴스로 요청해도 세션이 유지되는지 검증하는 테스트
- [ ] Redis 연결 실패·지연·메모리 사용량 모니터링 및 알림 구성
- [ ] Redis 접속 설정(호스트/DB/타임아웃)의 환경변수화 및 배포 문서 갱신

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 복원 기준점(ba84cb2) 시점의 프로세스 메모리 구현으로 되돌리고 `requirements.txt`에서 `redis==5.0.8`을 제거한다. 단 되돌리면 다중 인스턴스 로그인 풀림 문제가 그대로 재발한다.
- **Migration Cost:** Low

## Review Trigger

- 대화에서 명시된 재검토 조건이 없어 비워 둔다.

## References

- **Documentation:** `app/session.py`(현행 프로세스 메모리 세션 구현), `requirements.txt`(`redis==5.0.8` 추가)
