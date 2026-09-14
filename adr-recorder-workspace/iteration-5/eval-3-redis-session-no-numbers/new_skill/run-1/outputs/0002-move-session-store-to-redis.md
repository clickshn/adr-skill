# ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 세션 저장소를 앱 프로세스 메모리(dict)에서 Redis로 옮겨, 서버 여러 대가 같은 세션을 쓰도록 한다.
- **Scope:** member-portal / 세션 관리 (app/session.py)
- **Decision Source:** Human

---

## Context

### Problem

- 현재 세션은 `app/session.py`의 모듈 전역 dict(`_sessions`)에 저장된다. 이 방식은 세션이 각 서버 프로세스 안에만 존재한다.
- 서버를 3대로 늘리자, 로그인을 처리한 서버와 다른 서버로 다음 요청이 가면 세션을 찾지 못해 로그인이 풀리는 문제가 생겼다.
- 프로세스 메모리 저장 방식은 서버 재시작이나 재배포 때도 모든 세션이 사라진다(코드 구조에서 확인한 정성적 관찰).

### Constraints

- 스택: FastAPI 0.112.2 / uvicorn 0.30.6 / SQLAlchemy 2.0.32 (requirements.txt 기준).
- 세션 모듈은 `get(session_id)`와 `put(session_id, data)` 두 함수만 외부에 제공한다. 호출하는 쪽을 바꾸지 않으려면 이 시그니처를 그대로 둬야 한다.
- Redis 운영 형태(단일 인스턴스, 복제/클러스터, 매니지드 여부)는 아직 정해지지 않았다.

## Decision

### Selected

- **Technology:** Redis, Python 클라이언트 `redis==5.0.8` (redis-py, requirements.txt에 추가됨)
- **Architecture:** 세션 상태를 앱 서버 밖의 공유 저장소(Redis)로 옮긴다. 앱 서버 3대가 모두 같은 Redis에서 세션을 읽고 쓰므로, 앱 서버는 세션 상태를 갖지 않는다(stateless).
- **Implementation:** `app/session.py`의 `get`/`put` 인터페이스는 그대로 두고, 안쪽 저장소만 `_sessions` dict에서 Redis 클라이언트로 바꾼다.

## Rationale

1. 세션을 프로세스 밖 공유 저장소에 두면, 3대 중 어느 서버가 요청을 받든 같은 세션을 읽을 수 있다. 그래서 서버 증설 뒤 생긴 로그인 풀림 문제를 근본적으로 해결한다.
2. 지금 세션 모듈은 `session_id`로 dict를 넣고 꺼내는 key-value 구조라 Redis의 key-value 모델에 그대로 대응한다. 그래서 변경 범위를 `app/session.py` 한 파일로 줄일 수 있다.

## Consequences

### Positive

- 서버 대수와 상관없이 로그인 상태가 유지되므로, 앞으로 서버를 더 늘려도 세션 때문에 막히지 않는다.
- 앱 서버를 재시작하거나 재배포해도 Redis가 살아 있으면 세션이 남는다.
- Redis의 키 단위 TTL로 세션 만료를 저장소 차원에서 처리할 수 있다.

### Negative

- 운영할 인프라 구성요소(Redis)가 하나 늘어난다. 배포, 설정, 백업을 따로 관리해야 한다.
- 세션을 조회할 때마다 네트워크 왕복이 한 번 생긴다. 지금은 메모리에서 바로 읽는다.
- 지금 `put`은 Python dict를 그대로 저장하지만, Redis에 넣으려면 직렬화(예: JSON)가 필요하다. 그러면 직렬화할 수 없는 값은 세션에 넣을 수 없다.

### Risks

- 단일 장애점: Redis가 멈추면 3대 모두 세션을 조회하지 못해 서비스 전체에서 로그인이 안 된다. 가용성 구성을 따로 검토해야 한다.
- 전환 배포 시점에 프로세스 메모리에 있던 기존 세션이 모두 사라진다. 이때 로그인해 있던 사용자는 한 번 다시 로그인해야 한다.
- 세션에 인증 정보가 들어 있으므로, Redis 접근 제어(비밀번호/ACL, 네트워크 격리)가 빠지면 세션이 탈취될 위험이 있다.
- TTL을 설정하지 않으면 만료된 세션이 쌓여 Redis 메모리가 계속 늘어난다.

## Implementation

- [ ] `app/session.py`의 `_sessions` dict를 redis-py 클라이언트로 교체 (`get`/`put` 시그니처 유지, 세션 데이터 직렬화 방식 결정)
- [ ] 세션 키에 TTL 설정, 필요하면 로그아웃용 삭제 함수 추가
- [ ] Redis 접속 정보(호스트, 포트, 인증)를 환경변수나 설정으로 분리
- [ ] 테스트: 서로 다른 앱 인스턴스에서 같은 세션을 조회할 수 있는지, 로그인/로그아웃 흐름, Redis 연결 실패 시 동작
- [ ] 모니터링: Redis 가용성, 응답 지연, 메모리 사용량, 연결 수
- [ ] 문서/설정 업데이트: 배포 구성과 로컬 개발 환경에 Redis 추가

## Reversibility

- **Reversible:** Yes
- **Rollback:** `app/session.py`를 dict 기반 구현으로 되돌리고 requirements.txt에서 `redis==5.0.8`을 빼면 된다. 다만 되돌리면 Redis에 있던 세션이 사라지고(사용자 재로그인 필요), 서버가 여러 대인 환경에서는 로그인 풀림 문제가 다시 생긴다.
- **Migration Cost:** Low

## References

- **Documentation:** requirements.txt diff (`+redis==5.0.8`, 미커밋), 기존 구현 `app/session.py` (커밋 b540f01), 로그인/로그아웃 API 커밋 53eba24
