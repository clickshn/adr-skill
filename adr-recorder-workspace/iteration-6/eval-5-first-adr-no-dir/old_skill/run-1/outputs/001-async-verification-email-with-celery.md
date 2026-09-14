# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업으로 분리하고, 브로커로 기존 운영 중인 RabbitMQ를 사용한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`의 `send_verification`)
- **Decision Source:** Human

---

## Context

### Problem

현재 `send_verification`은 가입 요청 처리 중에 `smtplib.SMTP("smtp.internal", 25)`로 인증 메일을 동기 발송한다. 그래서 SMTP 서버가 느려지면 가입 API 응답도 그만큼 느려진다. 메일 발송 지연이 사용자 가입 경로에 그대로 옮겨오는 구조다.

### Constraints

- 브로커는 새 인프라 없이 이미 운영 중인 RabbitMQ를 써야 한다.
- 새 저장소나 미들웨어(예: Redis)를 추가로 운영하는 부담은 피한다.
- 서비스 스택: Python >= 3.11, FastAPI, SQLAlchemy 2.x (`pyproject.toml` 기준).

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, `pyproject.toml`에 추가됨), 브로커 RabbitMQ (기존 운영 인스턴스)
- **Architecture:** 가입 API는 인증 메일 작업을 큐에 넣기만 하고 바로 응답한다. 실제 SMTP 발송은 별도의 Celery 워커 프로세스가 비동기로 처리한다.
- **Implementation:** `send_verification`을 Celery task로 바꾸고, 가입 처리 코드에서는 직접 호출하는 대신 큐에 넣는 방식(`.delay()`/`.apply_async()`)으로 바꾼다.

## Rationale

1. SMTP 발송을 요청 경로 밖으로 빼서, SMTP 지연이 가입 API 응답 시간에 영향을 주지 않게 한다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓰므로 새로 운영할 인프라가 생기지 않는다.
3. RQ도 검토했지만 Redis를 새로 운영해야 해서 제외했다. Celery는 RabbitMQ를 브로커로 바로 쓸 수 있다.

## Alternatives

### RQ (Redis Queue)

- **Pros:** 작업 큐 기능을 제공하는 대안으로 검토됨
- **Cons:** 브로커로 Redis가 필요함
- **Rejected because:** Redis를 새로 운영해야 함 (현재 운영 중인 브로커는 RabbitMQ)
- **Recheck if:** Redis를 다른 목적으로 이미 운영하게 되거나, RabbitMQ 운영을 중단하게 될 경우

## Consequences

### Positive

- SMTP 지연이나 장애가 가입 API 응답 시간에 영향을 주지 않는다.
- 기존 RabbitMQ를 재사용하므로 인프라가 늘지 않는다.
- 메일 발송 실패 시 워커 쪽에서 재시도 정책을 적용할 수 있다.

### Negative

- Celery 워커 프로세스를 추가로 배포하고 운영해야 한다.
- 가입 API가 성공 응답을 준 뒤에 메일 발송이 실패할 수 있다. 발송 실패가 더 이상 API 응답으로 드러나지 않는다.

### Risks

- 워커가 멈추거나 큐가 쌓이면 인증 메일이 늦게 가거나 가지 않을 수 있다.
- 재시도나 ack 설정에 따라 인증 메일이 중복 발송될 수 있다.
- 작업 메시지에 인증 토큰이 들어가므로 브로커에 토큰이 남는다.

## Implementation

- [ ] 구현 작업: Celery 앱 설정(브로커 = 기존 RabbitMQ), `send_verification`을 task로 바꾸고 가입 처리 코드에서 큐에 넣도록 수정
- [ ] 테스트: 가입 API가 SMTP 호출 없이 작업만 넣고 응답하는지, 워커 task의 발송/재시도 동작 확인
- [ ] 모니터링: 큐 적체량, 작업 실패/재시도 건수, 워커 생존 상태
- [ ] 문서/설정 업데이트: 브로커 접속 정보 설정, 워커 실행/배포 방법

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리 코드에서 다시 `send_verification`을 직접(동기) 호출하도록 되돌리고, `pyproject.toml`에서 `celery` 의존성과 워커 배포를 제거한다. 호출 지점이 `app/mail.py`의 발송 함수 하나라서 되돌리는 범위가 작다.
- **Migration Cost:** Low

## Review Trigger

- Redis를 다른 목적으로 이미 운영하게 되거나, RabbitMQ 운영을 중단하게 될 경우 (RQ 재검토)

## References

- **Documentation:** 동기 발송 도입 커밋 `558ed63` (feat: 가입 인증 메일 발송), 대상 코드 `app/mail.py`, 의존성 변경 `pyproject.toml` (`celery>=5.4` 추가, 미커밋)
