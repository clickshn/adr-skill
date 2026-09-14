# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업(브로커: 기존 RabbitMQ)으로 분리한다
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

- 현재 `send_verification()`은 가입 요청 처리 중 `smtplib.SMTP("smtp.internal", 25)`로 인증 메일을 동기 발송한다.
- SMTP 서버가 느려지면 가입 API 응답도 같이 느려진다. (현 코드는 `smtplib.SMTP`에 timeout을 지정하지 않아 SMTP 지연이 요청 처리 시간에 그대로 더해진다.)

### Constraints

- 메시지 브로커로 쓸 RabbitMQ가 이미 운영 중이다.
- Redis는 운영하고 있지 않으며, 새 인프라를 추가로 운영하는 것은 피한다.
- 서비스는 Python 3.11+ / FastAPI 기반이다.

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, `pyproject.toml`에 추가됨), 브로커는 기존 RabbitMQ
- **Architecture:** 가입 API → Celery 작업 발행(RabbitMQ) → Celery 워커 → SMTP 발송. 가입 API는 메일 발송 완료를 기다리지 않는다.
- **Implementation:** `send_verification()`을 Celery 작업으로 등록하고, 가입 처리 코드에서는 작업을 큐에 넣기만 한다.

## Rationale

1. 메일 발송을 요청 처리 경로에서 떼어내면 SMTP 지연이 가입 API 응답 시간에 전파되지 않는다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓸 수 있어 새 인프라가 필요 없다.

## Alternatives

### RQ

- **Pros:** 작업 큐로서 요청 처리 경로에서 메일 발송을 분리할 수 있다.
- **Cons:** Redis를 브로커로 요구한다.
- **Rejected because:** Redis를 새로 운영해야 한다.
- **Recheck if:** Redis를 운영하게 되어 새 인프라 부담이 사라지는 경우

### 현행 유지 (요청 처리 중 동기 발송)

- **Pros:** 추가 의존성·워커 운영이 없다.
- **Cons:** SMTP가 느릴 때 가입 API까지 같이 느려진다.
- **Rejected because:** SMTP 지연이 가입 API 응답 지연으로 이어진다.

## Consequences

### Positive

- 가입 API 응답 시간이 SMTP 상태와 분리된다.
- 기존 RabbitMQ를 재사용해 추가 인프라 운영 부담이 없다.

### Negative

- Celery 워커 프로세스를 새로 배포·운영해야 한다.
- 메일 발송 실패가 가입 API 응답에 드러나지 않으므로 별도로 감지해야 한다.

### Risks

- 워커가 멈추거나 큐가 적체되면 인증 메일이 지연되거나 발송되지 않을 수 있다.
- RabbitMQ 장애 시 작업 발행이 실패하면 가입 흐름에 영향을 줄 수 있다.
- 작업 재시도 설정에 따라 인증 메일이 중복 발송될 수 있다.

## Implementation

- [x] `pyproject.toml`에 `celery>=5.4` 추가
- [ ] 구현 작업: Celery 앱 구성(RabbitMQ 브로커 연결), `send_verification`을 작업으로 전환, 가입 처리에서 작업 발행으로 교체
- [ ] 테스트: 가입 API가 SMTP 지연과 무관하게 응답하는지, 작업이 발행·처리되는지 확인
- [ ] 모니터링: 큐 적체, 작업 실패·재시도 현황
- [ ] 문서/설정 업데이트: 브로커 접속 설정, 워커 실행/배포 설정

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리에서 `send_verification()`을 다시 직접(동기) 호출하도록 되돌리고 `celery` 의존성과 워커를 제거한다. 워커 제거 전 큐에 남은 작업을 소진한다.
- **Migration Cost:** Low

## Review Trigger

- Redis를 운영하게 되어 새 인프라 부담이 사라지는 경우 (RQ 재검토)

## References

- **Documentation:** 현행 동기 발송 구현 커밋 `c44bbf9` (feat: 가입 인증 메일 발송), `app/mail.py`, `pyproject.toml` 의존성 변경(미커밋)
