# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 분리

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업(브로커: 기존 RabbitMQ)으로 비동기 발송한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

가입 요청 처리 중 `app/mail.py`의 `send_verification()`이 `smtplib`로 `smtp.internal:25`에 인증 메일을 동기 발송한다. 이 때문에 SMTP 서버가 느릴 때 가입 API 응답까지 같이 느려진다.

### Constraints

- 메시지 브로커는 이미 운영 중인 RabbitMQ를 사용한다.
- 브로커 때문에 새 인프라(Redis 등)를 추가로 운영하지 않는다.
- Python >= 3.11, FastAPI 기반 서비스 (`pyproject.toml`).

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, `pyproject.toml`에 추가됨), 브로커 RabbitMQ (기존 운영 중)
- **Architecture:** 가입 API는 인증 메일 발송 작업을 큐에 넣고 바로 응답한다. SMTP 발송은 별도 Celery 워커가 처리한다.
- **Implementation:** `send_verification()`을 Celery 태스크로 바꾸고, 가입 처리 경로에서는 직접 호출하지 않고 큐에 넣는다.

## Rationale

1. SMTP 발송을 요청 처리 경로에서 떼어 내면 SMTP가 느려도 가입 API 응답 시간은 영향을 받지 않는다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓰므로 새로 운영할 인프라가 생기지 않는다.
3. 검토한 RQ는 Redis를 새로 운영해야 하지만 Celery는 기존 RabbitMQ를 그대로 쓸 수 있다.

## Alternatives

### RQ (Redis Queue)

- **Cons:** Redis를 새로 운영해야 한다.
- **Rejected because:** 브로커용 Redis를 새로 도입·운영해야 해서 제외했다. 이미 운영 중인 RabbitMQ를 쓸 수 있는 Celery를 택했다.

### 현행 유지 (요청 처리 중 동기 발송)

- **Pros:** 추가 의존성과 워커 프로세스가 필요 없다.
- **Cons:** SMTP 지연이 가입 API 응답 지연으로 그대로 이어진다.
- **Rejected because:** SMTP가 느릴 때 가입 API까지 같이 느려지는 문제가 이번 결정의 출발점이다.

## Consequences

### Positive

- 가입 API 응답 시간이 SMTP 서버 상태의 영향을 받지 않는다.
- 새 브로커 인프라 없이 기존 RabbitMQ를 재사용한다.

### Negative

- Celery 워커 프로세스를 따로 배포하고 운영해야 한다.
- 발송이 비동기로 바뀌어 가입 API가 응답하는 시점에는 메일 발송 성공 여부를 알 수 없다.
- 런타임 의존성(`celery`)이 하나 늘어난다.

### Risks

- RabbitMQ 장애 시 작업을 큐에 넣지 못해 가입 흐름에 영향을 줄 수 있다.
- 워커가 멈추거나 처리량이 부족하면 인증 메일이 쌓이고 늦게 도착한다.
- 재시도를 설정하면 같은 인증 메일이 중복 발송될 수 있다.

## Implementation

- [ ] 구현 작업: `send_verification()`을 Celery 태스크로 바꾸고 가입 처리 경로에서 큐에 넣도록 변경 (현재 `app/mail.py`는 아직 `smtplib` 동기 발송)
- [ ] 구현 작업: Celery 앱과 RabbitMQ 브로커 연결 설정
- [ ] 테스트: 가입 API가 작업을 큐에 넣기만 하고 바로 응답하는지, 태스크가 메일을 실제로 발송하는지 확인
- [ ] 모니터링: 큐 적체량, 태스크 실패·재시도 수
- [ ] 문서/설정 업데이트: `pyproject.toml`의 `celery>=5.4` 추가분 커밋 (현재 미커밋), 워커 실행·배포 방법 문서화

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리 경로의 태스크 호출을 기존 동기 `send_verification()` 호출로 되돌리고(c44bbf9 구현), `pyproject.toml`에서 `celery`를 제거한다. 워커는 큐에 남은 작업을 모두 처리한 뒤 내린다.
- **Migration Cost:** Low

## References

- **Documentation:** c44bbf9 (`feat: 가입 인증 메일 발송`, 현행 동기 발송 구현), `pyproject.toml` (`celery>=5.4` 추가, 미커밋)
