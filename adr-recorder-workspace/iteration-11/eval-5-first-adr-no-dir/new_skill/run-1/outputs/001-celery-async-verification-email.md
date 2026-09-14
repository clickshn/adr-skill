# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업 큐(브로커: 기존 운영 중인 RabbitMQ)로 넘겨 비동기로 발송한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

회원가입 인증 메일을 가입 요청 처리 중에 동기로 발송하고 있어, SMTP 서버가 느려지면 가입 API 응답까지 같이 느려진다.
현재 `app/mail.py`의 `send_verification()`은 `smtplib.SMTP("smtp.internal", 25)`에 timeout 인자 없이 접속해 발송이 끝날 때까지 요청 처리 흐름을 붙잡는다.

### Constraints

- 메시지 브로커는 이미 운영 중인 RabbitMQ를 사용한다.
- 작업 큐 도입을 위해 새 인프라(Redis 등)를 추가로 운영하지 않는다.
- 기존 스택: Python >=3.11, FastAPI, SQLAlchemy (`pyproject.toml`).

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, `pyproject.toml` dependencies에 추가됨), 브로커 RabbitMQ
- **Architecture:** 가입 API는 인증 메일 발송 작업을 큐에 넣고 바로 응답하며, 실제 SMTP 발송은 별도 Celery 워커가 처리한다.
- **Implementation:** `app/mail.py`의 동기 `send_verification()` 호출 경로를 Celery task로 전환하고, 가입 처리 코드에서는 task를 enqueue만 한다.

## Rationale

1. SMTP 지연이 가입 API 응답 시간으로 전파되는 문제를 요청 처리 경로에서 메일 발송을 분리해 끊는다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓸 수 있어 새 인프라 운영 부담 없이 작업 큐를 도입할 수 있다.

## Alternatives

### 현행 유지 (요청 처리 중 동기 발송)

- **Pros:** 추가 의존성·워커 프로세스 없이 현재 코드 그대로 동작한다.
- **Cons:** SMTP 응답 속도에 가입 API 응답 시간이 종속된다.
- **Rejected because:** SMTP가 느릴 때 가입 API까지 같이 느려진다.

### RQ (Redis Queue)

- **Pros:** Python 작업 큐로서 선택지로 검토됨.
- **Cons:** 브로커로 Redis가 필요하다.
- **Rejected because:** Redis를 새로 운영해야 한다. 이미 운영 중인 RabbitMQ를 활용할 수 있는 Celery를 택했다.

## Consequences

### Positive

- SMTP 지연·장애가 가입 API 응답 시간에 직접 영향을 주지 않는다.
- 기존 RabbitMQ 인프라를 재사용한다.

### Negative

- Celery 워커 프로세스를 추가로 배포·운영해야 한다.
- 가입 API 응답 시점에는 메일 발송 성공 여부를 알 수 없다.

### Risks

- 워커 중단이나 발송 실패 시 인증 메일이 누락될 수 있으므로 재시도 정책과 실패 감지가 필요하다.
- 인증 토큰이 포함된 메일 내용(또는 토큰)이 브로커 메시지로 전달된다.

## Implementation

- [x] `pyproject.toml`에 `celery>=5.4` 추가 (미커밋 변경)
- [ ] 구현 작업: Celery 앱(브로커 RabbitMQ) 설정, `send_verification`을 task로 전환, 가입 처리에서 enqueue 호출
- [ ] 테스트: 가입 API가 SMTP 지연과 무관하게 응답하는지, task가 메일을 발송하는지 확인
- [ ] 모니터링: 큐 적체·task 실패/재시도 관측
- [ ] 문서/설정 업데이트: 워커 실행 방법과 브로커 접속 설정 문서화

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리에서 task enqueue 대신 기존 동기 `send_verification()` 호출로 되돌리고, 큐에 남은 작업을 소진한 뒤 워커를 내리고 `pyproject.toml`에서 `celery`를 제거한다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/mail.py` (현행 동기 발송 구현, 커밋 751f118에서 도입), `pyproject.toml` (`celery>=5.4` 추가, 미커밋 변경)
