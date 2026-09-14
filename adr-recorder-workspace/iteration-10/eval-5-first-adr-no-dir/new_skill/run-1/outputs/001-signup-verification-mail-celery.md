# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 분리

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업 큐(브로커: 기존 운영 중인 RabbitMQ)로 넘겨 비동기로 발송한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/mail.py`의 `send_verification()`은 가입 요청 처리 중에 `smtplib`로 `smtp.internal:25`에 직접 접속해 인증 메일을 동기 발송한다(커밋 c44bbf9). 그래서 SMTP 서버가 느려지면 가입 API 응답도 같이 느려진다.

### Constraints

- 메시지 브로커는 이미 운영 중인 RabbitMQ를 쓴다. Redis 같은 인프라를 새로 운영하는 것은 피한다.
- 프로젝트는 Python >=3.11, FastAPI 기반이다(`pyproject.toml`).

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`), 브로커 RabbitMQ(기존 운영 중)
- **Architecture:** 가입 API는 메일 발송 작업을 큐에 넣고 바로 응답하고, 별도 Celery 워커가 큐에서 작업을 꺼내 SMTP로 발송한다.
- **Implementation:** `send_verification()`을 Celery 태스크로 바꾸고, 가입 처리 경로에서는 큐 등록만 한다. 현재 `pyproject.toml`에 의존성만 추가됐고(미커밋), `app/mail.py`는 아직 동기 발송 코드 그대로다.

## Rationale

1. 메일 발송을 요청 처리 경로 밖으로 빼면 SMTP 지연이 가입 API 응답 시간에 전파되지 않는다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓸 수 있어서 새 인프라를 운영하지 않아도 된다.

## Alternatives

### 현행 유지 (요청 처리 중 동기 발송)

- **Pros:** 추가 의존성이나 워커 프로세스가 필요 없다.
- **Cons:** SMTP 응답 지연이 가입 API 응답 시간에 그대로 반영된다.
- **Rejected because:** SMTP가 느릴 때 가입 API까지 같이 느려진다.

### RQ

- **Cons:** 브로커로 Redis가 필요하다.
- **Rejected because:** Redis를 새로 운영해야 한다. 이미 운영 중인 RabbitMQ를 쓸 수 있는 Celery와 달리 인프라 부담이 늘어난다.

## Consequences

### Positive

- 가입 API 응답 시간이 SMTP 응답 속도에 묶이지 않는다.
- 기존 RabbitMQ를 재사용하므로 새 브로커 인프라가 필요 없다.

### Negative

- Celery 워커 프로세스를 따로 배포하고 운영해야 한다.
- 메일은 가입 응답 뒤에 발송되므로, 발송이 실패해도 가입 API 응답에는 드러나지 않는다.

### Risks

- 워커가 멈추거나 큐가 쌓이면 인증 메일이 늦게 가거나 빠질 수 있다.
- 재시도 설정에 따라 인증 메일이 두 번 이상 발송될 수 있다.

## Implementation

- [ ] Celery 앱 구성(RabbitMQ 브로커 URL 설정), `send_verification()`을 태스크로 전환, 가입 처리에서 큐 등록으로 호출 변경
- [ ] 테스트: 가입 API가 SMTP를 기다리지 않고 응답하는지, 태스크가 실제로 메일을 보내는지 확인
- [ ] 모니터링: 큐 적체와 태스크 실패 알림
- [ ] 문서/설정 업데이트: 워커 실행 방법, 브로커 접속 설정

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리에서 큐 등록 대신 `send_verification()`을 직접 호출하도록 되돌리고, `pyproject.toml`에서 `celery>=5.4`를 빼고, 워커를 내린다. RabbitMQ는 원래 운영 중이던 것이라 따로 걷어낼 필요가 없다.
- **Migration Cost:** Low

## References

- **Documentation:** 커밋 c44bbf9 (`feat: 가입 인증 메일 발송`, 현행 동기 발송을 추가한 `app/mail.py`), `pyproject.toml` 의존성 변경(`celery>=5.4`, 미커밋)
