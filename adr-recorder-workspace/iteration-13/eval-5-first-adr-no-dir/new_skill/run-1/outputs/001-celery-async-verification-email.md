# ADR-001: 회원가입 인증 메일을 Celery 작업 큐로 비동기 발송

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업 큐(브로커: 기존 RabbitMQ)로 분리한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송
- **Decision Source:** Human

---

## Context

### Problem

회원가입 인증 메일을 가입 요청 처리 경로 안에서 동기로 발송하고 있다(`app/mail.py`의 `send_verification`이 `smtplib`로 직접 SMTP 연결). 이 때문에 SMTP 서버가 느려지면 가입 API 응답까지 같이 느려진다.

### Constraints

- 메시지 브로커는 이미 운영 중인 RabbitMQ를 사용한다. 이 결정 때문에 새 인프라를 도입하지 않는다.
- 기존 스택(Python 3.11+, FastAPI, SQLAlchemy) 위에 붙일 수 있어야 한다.

## Decision

### Selected

- **Technology:** Celery `>=5.4` (pyproject.toml 의존성에 추가됨), 브로커는 운영 중인 RabbitMQ.
- **Architecture:** 가입 API는 인증 메일 발송을 큐에 넣고 즉시 응답하고, 실제 SMTP 발송은 Celery 워커가 처리한다.
- **Implementation:** `app/mail.py`의 `send_verification`을 Celery 태스크로 전환하고, 가입 요청 경로에서는 태스크 enqueue만 수행한다.

## Rationale

1. SMTP 지연이 가입 API 응답 시간으로 전파되는 경로를 끊는다.
2. 브로커로 이미 운영 중인 RabbitMQ를 그대로 재사용할 수 있어 추가 운영 부담이 없다.

## Alternatives

### RQ

- **Cons:** 브로커로 Redis가 필요한데 현재 운영 중이 아니다.
- **Rejected because:** Redis를 새로 운영해야 해서.

## Consequences

### Positive

- 가입 API 응답 시간이 SMTP 응답 속도와 분리된다.
- 이미 운영 중인 RabbitMQ를 쓰므로 새로 운영할 인프라가 없다.

### Negative

- Celery 워커라는 실행 구성요소가 늘어나 배포·운영 대상이 하나 추가된다.
- 메일 발송이 비동기가 되어 가입 직후 메일 도착까지 지연이 생길 수 있다.

### Risks

- 워커 중단이나 큐 적체 시 가입 API는 정상 응답하지만 인증 메일이 나가지 않아 장애 인지가 늦어질 수 있다.
- RabbitMQ 장애의 영향 범위가 가입 플로우까지 넓어진다.

## Implementation

- [ ] `app/mail.py`의 동기 발송을 Celery 태스크로 전환하고 가입 경로는 enqueue만 수행
- [ ] 태스크 enqueue 및 발송 경로 테스트
- [ ] 큐 적체·태스크 실패 모니터링
- [ ] Celery 워커 실행 방법과 브로커 설정 문서화

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 경로에서 태스크 enqueue를 `send_verification` 직접 호출로 되돌리고 pyproject.toml에서 celery 의존성을 제거한다(현재 HEAD `558ed63` 기준).
- **Migration Cost:** Low

## References

- **Documentation:** 현행 동기 발송 구현 `app/mail.py` (커밋 `ebfea45`)
