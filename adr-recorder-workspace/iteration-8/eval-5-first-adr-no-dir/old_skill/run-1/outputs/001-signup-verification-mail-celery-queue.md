# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 분리

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업(브로커: 기존 RabbitMQ)으로 분리해 비동기로 발송한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

회원가입 인증 메일을 가입 API 요청 처리 중에 동기로 발송하고 있어, SMTP가 느릴 때 가입 API 응답까지 함께 느려진다.
현재 `app/mail.py`의 `send_verification()`은 `smtplib.SMTP("smtp.internal", 25)`를 timeout 인자 없이 호출하므로 SMTP 지연이 그대로 요청 처리를 붙잡는다.

### Constraints

- 메시지 브로커는 이미 운영 중인 RabbitMQ를 사용한다. 새 인프라(Redis 등)를 따로 운영하지 않는다.
- Python >=3.11, FastAPI 기반 signup-api (`pyproject.toml`).

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, `pyproject.toml`에 추가됨), 브로커는 운영 중인 RabbitMQ
- **Architecture:** 가입 API는 인증 메일 발송 작업을 큐에 넣고 바로 응답한다. 별도 Celery 워커가 큐에서 작업을 꺼내 SMTP로 발송한다.
- **Implementation:** `send_verification()`의 SMTP 발송 로직을 Celery 태스크로 옮기고, 가입 처리 흐름에서는 태스크를 enqueue(`.delay()` 등)만 한다.

## Rationale

1. SMTP 발송을 요청 경로에서 떼어내면 SMTP가 느려도 가입 API 응답 시간이 영향을 받지 않는다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓰므로 인프라를 새로 운영할 필요가 없다.

## Alternatives

### RQ (Redis Queue)

- **Cons:** 브로커로 Redis가 필요해 Redis를 새로 운영해야 한다.
- **Rejected because:** 이미 운영 중인 RabbitMQ를 두고 Redis를 새로 운영해야 하는 부담이 생긴다.
- **Recheck if:** 다른 이유로 Redis를 운영하게 되어 새로 운영하는 부담이 없어지는 경우

## Consequences

### Positive

- SMTP가 느리거나 잠시 장애가 나도 가입 API 응답 시간에는 영향이 없다.
- 발송 실패를 워커 쪽에서 재시도할 수 있게 된다.

### Negative

- Celery 워커 프로세스를 새로 배포하고 운영해야 한다.
- 가입 API가 응답할 때 메일 발송이 끝났다는 보장이 없고, 발송 실패가 API 응답에 드러나지 않는다.

### Risks

- 워커가 멈추면 인증 메일이 큐에 쌓여 사용자가 메일을 늦게 받거나 받지 못한다.
- RabbitMQ 장애 시 enqueue 자체가 실패할 수 있으므로, 가입 처리 쪽에서 실패 시 어떻게 처리할지(오류 응답, 재발송 경로 등) 정해야 한다.
- 재시도 설정에 따라 인증 메일이 중복 발송될 수 있다.

## Implementation

- [x] `pyproject.toml`에 `celery>=5.4` 추가
- [ ] Celery 앱 구성(RabbitMQ 브로커 URL 설정) 및 `send_verification()`을 태스크로 전환
- [ ] 가입 API 처리 흐름에서 동기 호출을 태스크 enqueue로 교체
- [ ] 테스트: SMTP가 느려도 가입 API가 바로 응답하는지, 태스크 발송·재시도 동작 확인
- [ ] 모니터링: 큐 적체량, 태스크 실패·재시도 건수
- [ ] 문서/설정 업데이트: 워커 배포·실행 설정, 브로커 접속 정보

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 흐름의 태스크 enqueue를 기존 `send_verification()` 동기 호출로 되돌린다. 큐에 남은 작업을 워커로 모두 처리한 뒤 워커를 내리고, `pyproject.toml`에서 `celery` 의존성을 제거한다.
- **Migration Cost:** Low

## Review Trigger

- 다른 이유로 Redis를 운영하게 되어 새로 운영하는 부담이 없어지는 경우 (RQ 재검토)

## References

- **Documentation:** 동기 발송을 도입한 커밋 `c44bbf9` (feat: 가입 인증 메일 발송), 의존성 변경은 `pyproject.toml`(미커밋)
