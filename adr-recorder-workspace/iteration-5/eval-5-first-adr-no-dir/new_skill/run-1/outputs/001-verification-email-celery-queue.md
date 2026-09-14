# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 분리

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업(브로커: 기존 RabbitMQ)으로 비동기 발송한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/mail.py`의 `send_verification()`은 가입 요청 처리 중에 `smtplib.SMTP("smtp.internal", 25)`로 인증 메일을 동기 발송한다. 그래서 SMTP 서버가 느리면 가입 API 응답도 같이 느려진다. 메일 발송 지연이 가입 API 지연으로 그대로 이어지는 결합을 끊어야 한다.

### Constraints

- 새 인프라를 추가하지 않고, 이미 운영 중인 RabbitMQ를 브로커로 쓴다.
- 서비스 스택: Python >= 3.11, FastAPI, SQLAlchemy (`pyproject.toml`).

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, `pyproject.toml`에 추가), 브로커는 기존 RabbitMQ
- **Architecture:** 가입 API는 인증 메일 작업을 큐에 넣고 바로 응답한다. 실제 SMTP 발송은 별도 Celery 워커 프로세스가 맡는다.
- **Implementation:** 기존 `send_verification(to, token)`의 발송 로직을 Celery task로 감싸고, 가입 처리 코드는 동기 호출 대신 task를 enqueue(`.delay()` 등)하도록 바꾼다.

## Rationale

1. 가입 API 응답 시간을 SMTP 응답 속도와 분리해서, SMTP가 느려도 가입 API가 같이 느려지지 않게 한다.
2. 이미 운영 중인 RabbitMQ를 브로커로 재사용할 수 있어서 새 인프라 운영 부담이 없다.

## Alternatives

### RQ (Redis Queue)

- **Pros:** Python 작업 큐로서 비동기 메일 발송이라는 같은 목적을 달성할 수 있다.
- **Cons:** 브로커로 Redis가 필요하다.
- **Rejected because:** Redis를 새로 운영해야 한다. RabbitMQ는 이미 운영 중이다.
- **Recheck if:** 다른 목적으로 Redis를 운영하게 되어 새 인프라 부담이 없어질 때

## Consequences

### Positive

- SMTP 지연이 가입 API 응답 시간에 전파되지 않는다.
- 발송이 가입 요청과 분리돼서, 실패한 발송을 워커 쪽에서 재시도할 수 있다.

### Negative

- Celery 워커 프로세스를 따로 배포·운영해야 한다.
- 인증 메일이 가입 응답 뒤에 비동기로 발송되고, 발송 실패가 가입 API 응답에 드러나지 않는다.

### Risks

- 워커가 멈추면 인증 메일이 큐에 쌓이기만 하고 발송되지 않는다(가입자는 메일을 못 받음).
- 가입 API가 RabbitMQ에 의존하게 된다. 브로커 장애 시 enqueue 실패를 어떻게 처리할지 정해야 한다.
- 재시도 설정에 따라 같은 인증 메일이 중복 발송될 수 있다.

## Implementation

- [ ] 구현 작업: Celery 앱 생성(RabbitMQ broker URL 설정), `send_verification` 발송 로직을 task로 옮기기, 가입 처리 코드의 호출부를 enqueue로 바꾸기
- [ ] 테스트: task 단위 테스트(SMTP 모킹), 가입 API가 SMTP 호출 없이 응답하는지 확인
- [ ] 모니터링: 큐 적체 길이, 워커 생존 여부, task 실패/재시도 건수
- [ ] 문서/설정 업데이트: 워커 실행 방법과 배포 설정, broker URL 환경 변수

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리 코드의 호출부를 다시 `send_verification()` 동기 호출로 되돌리고 `pyproject.toml`에서 `celery`를 뺀다. 워커를 내리기 전에 큐에 남은 인증 메일 작업을 모두 처리(drain)한다.
- **Migration Cost:** Low

## Review Trigger

- 다른 목적으로 Redis를 운영하게 되어 새 인프라 부담이 없어질 때 (RQ 재검토)

## References

- **Documentation:** 기존 동기 발송 구현 커밋 `c5ffc58` (feat: 가입 인증 메일 발송) / `pyproject.toml`에 `celery>=5.4` 추가(미커밋 변경)
