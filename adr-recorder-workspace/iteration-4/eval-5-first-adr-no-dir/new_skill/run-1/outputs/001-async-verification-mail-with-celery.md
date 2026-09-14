# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업(브로커: 기존 RabbitMQ)으로 분리한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/mail.py`의 `send_verification()`은 가입 요청 처리 중에 `smtplib.SMTP("smtp.internal", 25)`로 인증 메일을 동기 발송한다. 그래서 SMTP 서버가 느려지면 가입 API 응답도 같이 느려진다. 메일 발송 지연이 가입 API 지연으로 그대로 이어지는 결합을 끊어야 한다.

### Constraints

- 메시지 브로커는 이미 운영 중인 RabbitMQ를 쓴다. 새 인프라(예: Redis)를 추가로 운영하지 않는다.
- 서비스 스택은 Python >= 3.11, FastAPI, SQLAlchemy 2.0이다.

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, `pyproject.toml`에 추가됨), 브로커는 기존 RabbitMQ
- **Architecture:** 가입 API는 인증 메일 작업을 큐에 넣고 바로 응답한다. 실제 SMTP 발송은 별도 Celery 워커 프로세스가 처리한다.
- **Implementation:** `send_verification()`을 Celery 태스크로 바꾸고, 가입 처리 경로에서는 동기 호출 대신 태스크 enqueue(`.delay()` 등)로 바꾼다.

## Rationale

1. SMTP 지연이 가입 API 응답 시간에 전파되지 않게 된다. 이 결정의 직접적인 목적이다.
2. 브로커로 이미 운영 중인 RabbitMQ를 쓰므로 새 인프라 운영 부담이 늘지 않는다.
3. Celery는 RabbitMQ(AMQP)를 브로커로 공식 지원하므로 기존 인프라와 바로 맞물린다.

## Alternatives

### RQ (Redis Queue)

- **Pros:** Celery보다 구성이 단순한 Python 작업 큐다.
- **Cons:** 브로커로 Redis가 필요하다.
- **Rejected because:** 현재 Redis를 운영하지 않고 있어서, RQ를 쓰려면 Redis를 새로 운영해야 한다.
- **Recheck if:** 다른 용도로 Redis를 운영하게 되어 추가 인프라 부담이 없어질 때

## Consequences

### Positive

- SMTP가 느리거나 일시적으로 장애가 나도 가입 API 응답 시간이 영향을 받지 않는다.
- 메일 발송 실패를 워커 쪽에서 재시도할 수 있게 된다.

### Negative

- Celery 워커 프로세스를 추가로 배포·운영해야 한다.
- 가입 API가 성공 응답을 준 시점에 메일이 실제로 발송됐다는 보장이 없다. 발송 실패가 API 호출자에게 보이지 않는다.

### Risks

- 워커가 멈추거나 RabbitMQ에 장애가 나면 가입은 성공하는데 인증 메일이 쌓이거나 유실될 수 있다.
- 재시도를 설정하면 같은 인증 메일이 중복 발송될 수 있다.
- 큐가 밀리면 인증 메일 도착이 늦어져 가입 완료율에 영향을 줄 수 있다.

## Implementation

- [ ] 구현 작업: RabbitMQ 브로커 URL로 Celery 앱을 설정하고, `send_verification()`을 태스크로 바꾸고, 가입 처리 경로에서 enqueue하도록 수정
- [ ] 테스트: 가입 API가 SMTP 호출 없이 응답하는지, 태스크가 SMTP 실패 시 재시도하는지 확인
- [ ] 모니터링: 큐 적체 길이, 태스크 실패·재시도 횟수, 워커 생존 여부
- [ ] 문서/설정 업데이트: 워커 실행 방법과 브로커 연결 설정을 배포 설정에 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리 경로에서 `send_verification()`을 다시 동기로 직접 호출하도록 되돌리고(4304a04 시점 구현), 워커를 내리고 `pyproject.toml`에서 `celery`를 제거한다. 되돌리기 전에 큐에 남은 메일 작업은 먼저 비워야 한다.
- **Migration Cost:** Low

## Review Trigger

- 다른 용도로 Redis를 운영하게 되어 추가 인프라 부담이 없어질 때 (RQ 재검토)

## References

- **Documentation:** 4304a04 (feat: 가입 인증 메일 발송 — 현재 동기 발송 구현), `app/mail.py`, `pyproject.toml`의 `celery>=5.4` 추가(미커밋 변경)
