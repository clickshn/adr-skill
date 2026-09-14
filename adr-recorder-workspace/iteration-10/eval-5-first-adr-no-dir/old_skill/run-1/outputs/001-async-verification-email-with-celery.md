# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 분리

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업 큐(브로커: 기존 RabbitMQ)로 넘겨 비동기로 발송한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`의 `send_verification`)
- **Decision Source:** Human

---

## Context

### Problem

회원가입 인증 메일을 가입 요청 처리 중에 동기로 발송하고 있어서, SMTP 서버가 느려지면 가입 API 응답도 같이 느려진다.
현재 `app/mail.py`의 `send_verification`은 `smtplib.SMTP("smtp.internal", 25)`에 timeout 없이 연결하므로 SMTP 지연이 요청 스레드에 그대로 전파된다.

### Constraints

- 브로커는 이미 운영 중인 RabbitMQ를 쓴다. 새 인프라(예: Redis)를 추가로 운영하지 않는다.
- 기존 스택: Python >=3.11, FastAPI, SQLAlchemy (`pyproject.toml`)

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, `pyproject.toml`에 추가됨), 브로커 RabbitMQ (기존 운영 중)
- **Architecture:** 가입 API는 인증 메일 발송 작업을 큐에 넣고 바로 응답한다. 실제 SMTP 발송은 별도 Celery 워커가 처리한다.
- **Implementation:** `send_verification`을 Celery task로 옮기고, 가입 요청 처리 경로에서는 동기 호출 대신 작업을 큐에 넣는다.

## Rationale

1. SMTP 발송을 요청 처리 경로에서 떼어내면 SMTP 지연이 가입 API 응답 시간으로 번지지 않는다.
2. 이미 운영 중인 RabbitMQ를 브로커로 재사용하므로 새 인프라를 운영할 필요가 없다.

## Alternatives

### RQ (Redis Queue)

- **Pros:** 작업 큐로 발송을 비동기화한다는 목적은 똑같이 달성할 수 있다.
- **Cons:** 브로커로 Redis가 필요하다.
- **Rejected because:** Redis를 새로 운영해야 해서 뺐다.

### 현행 유지 (요청 처리 중 동기 발송)

- **Pros:** 워커나 브로커 없이 구조가 단순하다.
- **Cons:** SMTP가 느리면 가입 API도 같이 느려진다.
- **Rejected because:** 이 ADR의 문제(SMTP 지연이 가입 API 지연으로 전파)를 해결하지 못한다.

## Consequences

### Positive

- 가입 API 응답 시간이 SMTP 응답 속도와 분리된다.
- 새 인프라 없이 기존 RabbitMQ로 비동기 처리 기반을 마련한다.

### Negative

- Celery 워커 프로세스를 따로 배포하고 운영해야 한다.
- 가입 응답 시점에는 메일 발송 성공 여부를 알 수 없어서, 발송 실패를 요청 안에서 바로 사용자에게 알릴 수 없다.

### Risks

- 워커가 멈추거나 큐가 쌓이면 인증 메일이 늦게 가거나 가지 않을 수 있다.
- 재시도나 재전달이 일어나면 인증 메일이 중복 발송될 수 있다.
- 가입 흐름이 RabbitMQ 가용성에 의존하게 된다.

## Implementation

- [x] `pyproject.toml`에 `celery>=5.4` 추가 (커밋 전)
- [ ] 구현 작업: Celery 앱과 RabbitMQ 브로커 연결 설정, `send_verification`을 task로 전환, 가입 API에서 작업을 큐에 넣도록 변경
- [ ] 테스트: 가입 API가 SMTP 지연과 무관하게 응답하는지, 워커에서 메일이 실제로 발송되는지 확인
- [ ] 모니터링: 큐 적체, 작업 실패와 재시도, 워커 상태
- [ ] 문서/설정 업데이트: 워커 실행 방법과 브로커 접속 설정

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 API에서 작업을 큐에 넣는 대신 `send_verification`을 다시 직접 호출한다. 큐에 남은 작업을 워커로 모두 처리한 뒤 워커를 내리고, `pyproject.toml`에서 `celery`를 뺀다. RabbitMQ는 원래 운영 중이던 것이라 따로 걷어낼 인프라가 없다.
- **Migration Cost:** Low

## References

- **Documentation:** 현행 동기 발송 코드는 `app/mail.py`(커밋 8ca7a94 `feat: signup-api 초기 구성`에서 추가됨), 의존성 변경은 `pyproject.toml`(작업 트리 변경, 커밋 전)
