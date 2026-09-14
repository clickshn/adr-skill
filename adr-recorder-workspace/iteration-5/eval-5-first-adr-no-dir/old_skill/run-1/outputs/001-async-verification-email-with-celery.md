# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업으로 분리하고, 브로커로 기존 운영 중인 RabbitMQ를 사용한다.
- **Scope:** signup-api / 가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/mail.py`의 `send_verification()`은 가입 요청을 처리하는 중에 `smtplib.SMTP("smtp.internal", 25)`로 인증 메일을 동기 발송한다. 그래서 SMTP 서버가 느려지면 가입 API 응답도 같이 느려진다. 현재 코드에는 SMTP 연결 timeout도 지정되어 있지 않다.

### Constraints

- 메시지 브로커로 이미 운영 중인 RabbitMQ를 쓴다. 새 인프라를 추가로 운영하는 부담은 피한다.
- 서비스 스택은 Python >=3.11, FastAPI, SQLAlchemy 기반이다(`pyproject.toml`).

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`), 브로커는 RabbitMQ
- **Architecture:** 가입 API는 인증 메일 발송 작업을 큐에 넣고 바로 응답한다. 실제 SMTP 발송은 별도 Celery worker가 처리한다.
- **Implementation:** `pyproject.toml` 의존성에 `celery>=5.4`를 추가했다. `send_verification()`을 Celery task로 감싸고, 가입 처리 경로에서는 직접 호출하는 대신 `.delay()`/`.apply_async()`로 넣는다.

## Rationale

1. SMTP 지연과 가입 API 응답 시간을 분리해서, 메일 서버가 느려도 가입 API가 같이 느려지지 않게 한다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓰면 새 인프라를 도입하지 않아도 된다.

## Alternatives

### RQ (Redis Queue)

- **Pros:** Python 작업 큐로 쓸 수 있는 선택지로 검토했다.
- **Cons:** Redis를 브로커로 써야 한다.
- **Rejected because:** Redis를 새로 운영해야 한다. 이미 운영 중인 RabbitMQ를 쓸 수 있는 Celery가 운영 부담이 적다.
- **Recheck if:** Redis를 다른 이유로 운영하게 되거나, RabbitMQ 운영을 중단할 때

## Consequences

### Positive

- SMTP가 느리거나 장애가 나도 가입 API 응답 시간에 직접 영향을 주지 않는다.
- 발송 작업을 worker에서 재시도할 수 있다.

### Negative

- Celery worker 프로세스를 추가로 배포하고 운영해야 한다.
- 가입 API 응답 시점에는 메일이 실제로 발송됐는지 알 수 없다.

### Risks

- worker가 멈추거나 큐가 쌓이면 인증 메일이 늦게 가거나 가지 않을 수 있다.
- 재시도 설정에 따라 인증 메일이 중복 발송될 수 있다.
- RabbitMQ 장애가 가입 흐름(메일 발송 작업 등록)에 영향을 준다.

## Implementation

- [ ] Celery 앱 구성(RabbitMQ 브로커 URL) 및 `send_verification`을 task로 전환
- [ ] 가입 처리 경로에서 동기 호출을 task 등록으로 교체
- [ ] 테스트: task 등록 및 worker 발송 동작 검증
- [ ] 모니터링: 큐 적체, task 실패/재시도 지표
- [ ] 문서/설정 업데이트: worker 실행 방법, 브로커 설정

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리 경로에서 task 등록 대신 `send_verification()`을 다시 직접 호출하고, `pyproject.toml`에서 `celery` 의존성과 worker 배포를 제거한다.
- **Migration Cost:** Low

## Review Trigger

- Redis를 다른 이유로 운영하게 되거나, RabbitMQ 운영을 중단할 때 (RQ 재검토)

## References

- **Documentation:** 기존 동기 발송 도입 커밋 `c5ffc58` (feat: 가입 인증 메일 발송), 대상 코드 `app/mail.py`
