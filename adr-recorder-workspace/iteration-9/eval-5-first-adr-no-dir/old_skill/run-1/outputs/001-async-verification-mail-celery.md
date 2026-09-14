# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업(브로커: 기존 운영 중인 RabbitMQ)으로 분리한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

`app/mail.py`의 `send_verification()`은 가입 요청 처리 중에 `smtplib`로 `smtp.internal:25`에 직접 접속해 메일을 동기로 보낸다. 그래서 SMTP 서버가 느려지면 가입 API 응답도 같이 느려진다. `smtplib.SMTP(...)` 호출에 timeout 인자가 없어서, SMTP 쪽 지연이 요청 지연으로 그대로 전파된다.

### Constraints

- 새 인프라를 따로 운영하지 않는다. 브로커는 이미 운영 중인 RabbitMQ를 쓴다.
- 기존 스택은 Python >=3.11, FastAPI, SQLAlchemy 2.0이다(`pyproject.toml`).

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, `pyproject.toml`에 추가됨), 브로커는 기존 RabbitMQ
- **Architecture:** 가입 API는 메일 발송 작업을 큐에 넣고 바로 응답한다. 실제 SMTP 발송은 별도 Celery 워커가 처리한다.
- **Implementation:** `send_verification`을 Celery task로 바꾸고, 가입 처리 경로에서는 직접 호출하는 대신 task를 enqueue한다(`.delay()` 등).

## Rationale

1. 가입 요청 경로에서 SMTP 호출을 빼서, SMTP가 느려져도 가입 API 응답 시간에 영향이 없게 한다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓰면 새로 운영할 인프라가 생기지 않는다.

## Alternatives

### RQ (Redis Queue)

- **Cons:** 브로커로 Redis가 필요한데, 현재 운영 중인 Redis가 없어서 새로 운영해야 한다.
- **Rejected because:** Redis를 새로 운영하는 부담이 생긴다. 이미 운영 중인 RabbitMQ를 쓸 수 있는 Celery로 충분하다.
- **Recheck if:** 다른 목적으로 Redis를 운영하게 되어 Redis 운영 부담이 더 이상 추가 비용이 아니게 될 때

## Consequences

### Positive

- SMTP 지연이나 장애가 가입 API 응답 시간으로 전파되지 않는다.
- 발송 실패를 워커 쪽 재시도로 처리할 수 있다.

### Negative

- Celery 워커 프로세스를 새로 배포하고 운영해야 한다.
- 가입 API가 응답하는 시점에는 메일 발송 성공 여부를 알 수 없다.

### Risks

- RabbitMQ 장애나 연결 지연이 생기면 enqueue 단계에서 가입 API가 영향을 받거나 발송 작업이 쌓일 수 있다.
- 작업이 재전달·재시도되면 인증 메일이 중복으로 발송될 수 있다.
- 인증 토큰이 브로커 메시지에 담기므로, 큐 접근 권한과 메시지 보존 정책을 관리해야 한다.

## Implementation

- [x] `pyproject.toml`에 `celery>=5.4` 의존성 추가
- [ ] Celery 앱 구성(RabbitMQ 브로커 URL 설정)
- [ ] `send_verification`을 Celery task로 전환하고 가입 처리 경로에서 enqueue하도록 변경
- [ ] SMTP 연결 timeout과 task 재시도 정책 설정
- [ ] Celery 워커 배포 구성
- [ ] 테스트(task enqueue와 발송 로직 단위 테스트)
- [ ] 모니터링(큐 적체 길이, task 실패·재시도 수)
- [ ] 문서/설정 업데이트(브로커 접속 정보, 워커 실행 방법)

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리 경로에서 task enqueue 대신 `send_verification()`을 직접 호출하도록 되돌리고, 워커를 내린 뒤 `pyproject.toml`에서 `celery`를 제거한다. 브로커는 기존 RabbitMQ라 인프라를 철거할 필요가 없다. 전환 시점에 큐에 남은 작업은 먼저 소진한다.
- **Migration Cost:** Low

## Review Trigger

- 다른 목적으로 Redis를 운영하게 되어 Redis 운영 부담이 더 이상 추가 비용이 아니게 될 때 (RQ 재검토)

## References

- **Documentation:** 동기 발송 구현 커밋 `c44bbf9` (feat: 가입 인증 메일 발송), 의존성 변경 `pyproject.toml` (`celery>=5.4` 추가, 미커밋)
