# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업으로 분리하고, 브로커는 이미 운영 중인 RabbitMQ를 사용한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송
- **Decision Source:** Human

---

## Context

### Problem

현재 회원가입 API는 요청 처리 흐름 안에서 인증 메일을 SMTP로 동기 발송한다. 그래서 SMTP 서버가 느려지면 가입 API 응답도 같이 느려진다.

### Constraints

- 메시지 브로커는 새로 도입하지 않고 이미 운영 중인 RabbitMQ를 쓴다.
- 새 인프라(예: Redis)를 추가로 운영하지 않는다.

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`), 브로커는 기존 RabbitMQ
- **Architecture:** 가입 API는 인증 메일 발송 작업을 큐에 넣고 바로 응답한다. 실제 SMTP 발송은 별도 Celery 워커가 처리한다.
- **Implementation:** `pyproject.toml`에 `celery>=5.4` 추가. 기존 메일 발송 로직(`app/mail.py`)을 Celery task로 전환한다.

## Rationale

1. SMTP 발송을 요청 경로 밖으로 빼면 SMTP 지연이 가입 API 응답 시간에 전파되지 않는다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓰므로 새 인프라 운영 부담이 없다.

## Alternatives

### RQ (Redis Queue)

- **Pros:** Python 작업 큐로 쓸 수 있는 대안.
- **Cons:** 브로커로 Redis가 필요하다.
- **Rejected because:** Redis를 새로 운영해야 한다. RabbitMQ는 이미 운영 중이다.
- **Recheck if:** Redis를 다른 용도로 도입해 운영하게 되는 경우

## Consequences

### Positive

- SMTP가 느려도 가입 API 응답 시간에 영향이 없다.
- 기존 RabbitMQ를 재사용해서 인프라가 늘지 않는다.

### Negative

- Celery 워커 프로세스를 따로 배포·운영해야 한다.
- 가입 응답 시점에는 메일 발송 성공 여부를 알 수 없다.

### Risks

- 워커나 브로커가 장애를 겪으면 인증 메일 발송이 지연되거나 누락될 수 있다.
- 재시도 설정에 따라 인증 메일이 중복으로 발송될 수 있다.

## Implementation

- [x] `pyproject.toml`에 `celery>=5.4` 의존성 추가
- [ ] `app/mail.py`의 인증 메일 발송을 Celery task로 전환하고, 가입 API에서는 task만 enqueue
- [ ] RabbitMQ 브로커 연결 설정과 Celery 워커 배포 구성
- [ ] 테스트: 가입 API가 SMTP 지연과 무관하게 응답하는지, task가 메일을 발송하는지
- [ ] 모니터링: 큐 적체, task 실패·재시도 건수

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 API에서 task enqueue 대신 기존 동기 발송 함수를 직접 호출하도록 되돌리고 워커를 내린다.
- **Migration Cost:** Low

## Review Trigger

- Redis를 다른 용도로 도입해 운영하게 되는 경우 (RQ 재검토)

## References

- **Documentation:** 기존 동기 발송 구현 커밋 `1c47568` (feat: 가입 인증 메일 발송). `pyproject.toml`의 `celery>=5.4` 추가는 아직 커밋 전.
