# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업 큐(브로커: 기존 운영 중인 RabbitMQ)로 옮긴다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

인증 메일이 가입 요청 처리 흐름 안에서 동기로 발송된다. 그래서 SMTP 서버가 느려지면 가입 API 응답도 같이 느려진다. 현재 `app/mail.py`의 `send_verification()`은 `smtplib.SMTP("smtp.internal", 25)`에 타임아웃 없이 직접 연결해서 보내므로, SMTP가 지연되는 만큼 요청 스레드가 그대로 붙잡혀 있다.

### Constraints

- 메시지 브로커는 이미 운영 중인 RabbitMQ를 쓴다. 이 결정 때문에 새 인프라를 늘리지 않는다.
- Python >=3.11, FastAPI 기반 서비스(`pyproject.toml`).

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`), 브로커는 기존 RabbitMQ
- **Architecture:** 가입 API는 메일 발송 작업을 큐에 넣고 바로 응답한다. 실제 SMTP 발송은 별도 Celery 워커 프로세스가 맡는다.
- **Implementation:** `pyproject.toml`에 `celery>=5.4` 추가 완료. `send_verification()`은 아직 동기 함수 그대로라서 Celery task로 바꾸는 작업이 남아 있다.

## Rationale

1. SMTP 지연이 가입 API 응답 시간에 번지지 않게 메일 발송을 요청 경로에서 떼어낸다.
2. 이미 운영 중인 RabbitMQ를 브로커로 바로 쓸 수 있어 추가 인프라 운영 부담이 없다.

## Alternatives

### RQ (Redis Queue)

- **Cons:** 브로커로 Redis가 필요한데, 현재 Redis는 운영하고 있지 않다.
- **Rejected because:** 이 용도 하나 때문에 Redis를 새로 운영해야 한다. 이미 운영 중인 RabbitMQ를 쓸 수 있는 Celery가 추가 인프라 없이 같은 목적을 이룬다.
- **Recheck if:** 다른 이유로 Redis를 운영하게 되는 경우

## Consequences

### Positive

- SMTP 지연이나 장애가 가입 API 응답 시간에 영향을 주지 않는다.
- 이후 다른 비동기 작업도 같은 Celery/RabbitMQ 경로에 올릴 수 있다.

### Negative

- Celery 워커 프로세스를 새로 배포하고 운영해야 한다.
- 가입 API 응답 시점에는 메일 발송 성공 여부를 알 수 없다.

### Risks

- 워커가 멈추거나 큐가 쌓이면 인증 메일이 늦게 가거나 유실될 수 있어서, 재시도와 모니터링이 필요하다.
- RabbitMQ에 장애가 나면 작업을 큐에 넣는 단계에서 가입 흐름이 실패할 수 있다.

## Implementation

- [ ] 구현 작업: Celery 앱 설정(브로커 = 기존 RabbitMQ), `send_verification`을 Celery task로 전환하고 가입 처리부에서 큐에 넣도록 변경, SMTP 실패 시 재시도 정책 설정
- [ ] 테스트: task 등록·실행, SMTP 실패 시 재시도 동작, 가입 API가 SMTP 지연과 무관하게 응답하는지 확인
- [ ] 모니터링: 큐 적체량, task 실패/재시도 횟수, 워커 상태
- [ ] 문서/설정 업데이트: 워커 실행·배포 설정, 브로커 접속 정보 설정

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리부가 `send_verification()`을 다시 직접(동기) 호출하게 되돌리고, `pyproject.toml`에서 `celery` 의존성을 제거한 뒤 워커를 내린다.
- **Migration Cost:** Low

## Review Trigger

- 다른 이유로 Redis를 운영하게 되는 경우 (RQ 재검토)

## References

- **Documentation:** `app/mail.py` (현재 동기 발송 구현, 커밋 ebfea45), `pyproject.toml` (`celery>=5.4` 추가, 미커밋 변경)
