# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업 큐(브로커: 기존 운영 중인 RabbitMQ)로 분리해 비동기로 발송한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (app/mail.py)
- **Decision Source:** Human

---

## Context

### Problem

회원가입 인증 메일을 가입 요청 처리 중에 동기로 SMTP 발송하고 있어, SMTP 응답이 느려지면 가입 API 응답까지 같이 느려진다.

### Constraints

- 새 인프라(예: Redis)를 추가로 운영하지 않고, 이미 운영 중인 RabbitMQ를 활용한다.
- 기존 스택: Python >= 3.11, FastAPI, SQLAlchemy (pyproject.toml)

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, pyproject.toml에 추가), 브로커는 기존 운영 중인 RabbitMQ
- **Architecture:** 가입 API는 인증 메일 발송 작업을 큐에 등록한 뒤 바로 응답하고, 별도 Celery 워커가 SMTP 발송을 수행한다.
- **Implementation:** 인증 메일 발송 로직(app/mail.py)을 Celery task로 전환하고, 가입 처리 경로에서는 작업 등록만 한다.

## Rationale

1. SMTP 발송을 가입 요청 처리 경로에서 떼어내면 SMTP 지연이 가입 API 응답 시간에 전파되지 않는다.
2. Celery는 RabbitMQ를 브로커로 쓸 수 있어, 이미 운영 중인 RabbitMQ를 그대로 활용하고 신규 인프라 운영 부담이 생기지 않는다.

## Alternatives

### RQ (Redis Queue)

- **Pros:** Celery보다 구성과 API가 단순한 Python 작업 큐
- **Cons:** 브로커로 Redis가 필요한데, 현재 Redis는 운영하지 않는다.
- **Rejected because:** Redis를 새로 도입·운영해야 한다. 이미 운영 중인 RabbitMQ를 쓸 수 있는 Celery로 추가 인프라 없이 같은 목적을 달성할 수 있다.
- **Recheck if:** Redis를 다른 용도로 운영하게 되거나, RabbitMQ 운영을 중단·교체하게 되는 경우

## Consequences

### Positive

- 가입 API 응답 시간이 SMTP 상태와 분리된다.
- 기존 RabbitMQ를 재사용하므로 새로 운영할 인프라가 없다.

### Negative

- Celery 워커 프로세스를 따로 배포·운영해야 한다.
- 발송이 비동기가 되어, 가입 응답 시점에는 인증 메일 발송 성공 여부를 알 수 없다.

### Risks

- 워커 중단이나 큐 적체 시 인증 메일이 늦게 가거나 누락되어 사용자가 인증을 완료하지 못할 수 있다.
- SMTP 실패 시 재시도 정책이 없으면 메일이 유실되고, 재시도 시에는 중복 발송이 생길 수 있다.
- RabbitMQ 장애 시 작업 등록이 실패하면 가입 흐름에 영향이 갈 수 있으므로 등록 실패 처리가 필요하다.

## Implementation

- [ ] 구현 작업: 인증 메일 발송 로직을 Celery task로 전환, Celery 앱(RabbitMQ 브로커 URL) 및 워커 실행 구성, 재시도 정책 설정
- [ ] 테스트: task 단위 테스트, 가입 API가 SMTP 호출 없이 응답하는지 확인
- [ ] 모니터링: 큐 길이, task 실패·재시도 수, 발송 지연
- [ ] 문서/설정 업데이트: 워커 배포·실행 방법, 브로커 접속 설정

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리에서 task 등록 대신 기존 동기 발송 함수를 직접 호출하도록 되돌리고, 워커와 `celery` 의존성을 제거한다.
- **Migration Cost:** Low

## Review Trigger

- Redis를 다른 용도로 운영하게 되는 경우 (RQ 재검토)
- RabbitMQ 운영을 중단하거나 다른 브로커로 교체하는 경우

## References

- **Documentation:** 기존 동기 발송 구현 커밋 `9ef6bd8` (feat: 가입 인증 메일 발송), 의존성 변경 `pyproject.toml` (`celery>=5.4` 추가, 미커밋)
