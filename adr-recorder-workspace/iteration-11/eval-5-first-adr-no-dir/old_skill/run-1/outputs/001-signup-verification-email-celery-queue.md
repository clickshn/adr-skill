# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업 큐(브로커: 기존 RabbitMQ)로 분리한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (app/mail.py)
- **Decision Source:** Human

---

## Context

### Problem

회원가입 인증 메일을 가입 요청 처리 중에 동기로 발송하고 있어, SMTP 서버가 느릴 때 가입 API 응답까지 함께 느려진다. 현재 `app/mail.py`의 `send_verification`이 요청 경로 안에서 `smtplib.SMTP("smtp.internal", 25)`로 직접 발송한다(커밋 286b20c).

### Constraints

- 메시지 브로커는 이미 운영 중인 RabbitMQ를 사용한다.
- Redis 등 새 인프라를 추가로 운영하지 않는다.
- 기존 스택: Python >=3.11, FastAPI, SQLAlchemy.

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`), 브로커 RabbitMQ(기존 운영 중)
- **Architecture:** 가입 API는 인증 메일 발송 작업을 큐에 넣고 바로 응답하며, 실제 SMTP 발송은 Celery 워커가 처리한다.
- **Implementation:** `pyproject.toml`에 `celery>=5.4` 추가(완료). `send_verification`을 Celery 작업으로 전환하고 가입 처리에서 작업을 큐에 넣도록 변경한다.

## Rationale

1. SMTP 발송을 요청 경로에서 분리하면 SMTP 지연이 가입 API 응답 시간으로 전파되지 않는다.
2. 이미 운영 중인 RabbitMQ를 Celery 브로커로 그대로 쓸 수 있어 새 인프라가 필요 없다.
3. RQ는 Redis를 새로 운영해야 해서 제약 조건에 맞지 않는다.

## Alternatives

### RQ (Redis Queue)

- **Cons:** 브로커로 Redis가 필요하다.
- **Rejected because:** Redis를 새로 운영해야 해서 제외했다.

### 현행 유지 (요청 처리 중 동기 발송)

- **Pros:** 추가 의존성·워커 없이 단순하다.
- **Cons:** SMTP 지연이 가입 API 응답에 그대로 전파된다.
- **Rejected because:** SMTP가 느릴 때 가입 API까지 함께 느려지는 문제가 이번 결정의 원인이다.

## Consequences

### Positive

- 가입 API 응답 시간이 SMTP 지연과 분리된다.
- 기존 RabbitMQ를 재사용하므로 신규 인프라 운영 부담이 없다.

### Negative

- Celery 워커 프로세스를 별도로 배포·운영해야 한다.
- 가입 응답 시점에는 인증 메일 발송 성공 여부를 알 수 없다.

### Risks

- 워커 중단이나 큐 적체 시 인증 메일 도착이 지연될 수 있다.
- RabbitMQ 장애 시 작업 등록이 실패해 가입 흐름에 영향을 줄 수 있다.
- 발송 실패 작업의 재시도 정책이 없으면 인증 메일이 유실될 수 있다.

## Implementation

- [x] `pyproject.toml`에 `celery>=5.4` 의존성 추가
- [ ] Celery 앱 및 RabbitMQ 브로커 연결 설정
- [ ] `app/mail.py`의 `send_verification`을 Celery 작업으로 전환하고 가입 처리에서 큐에 등록
- [ ] 테스트 (작업 등록 및 워커 발송 경로)
- [ ] 모니터링 (워커 상태, 큐 적체, 발송 실패/재시도)
- [ ] 문서/설정 업데이트 (워커 실행 방법, 브로커 접속 설정)

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리에서 `send_verification`을 다시 동기 호출하도록 되돌리고, Celery 워커를 중지한 뒤 `pyproject.toml`에서 `celery` 의존성을 제거한다.
- **Migration Cost:** Low

## References

- **Documentation:** 커밋 286b20c (현행 동기 발송 구현, `app/mail.py`), `pyproject.toml` celery 추가(미커밋 변경)
