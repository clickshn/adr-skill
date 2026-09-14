# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업(브로커: 기존 RabbitMQ)으로 분리한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

`send_verification()`이 가입 요청 처리 흐름 안에서 `smtplib.SMTP("smtp.internal", 25)`로 메일을 동기 발송한다. 그래서 SMTP 서버가 느려지면 가입 API 응답까지 함께 느려진다. 게다가 현재 코드는 SMTP 연결에 timeout을 지정하지 않아서, SMTP가 멈추면 요청이 무기한 대기할 수 있다.

### Constraints

- 브로커는 이미 운영 중인 RabbitMQ를 재사용한다. 메일 비동기화 때문에 새 인프라를 늘리지 않는다.
- 기존 스택은 Python >=3.11, FastAPI, SQLAlchemy다.

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, `pyproject.toml`에 추가됨), 브로커 RabbitMQ(AMQP)
- **Architecture:** 가입 API는 인증 메일 작업을 큐에 넣고 바로 응답한다. 실제 SMTP 발송은 별도 Celery 워커 프로세스가 맡는다.
- **Implementation:** `send_verification`을 Celery task로 전환하고, 가입 처리 코드는 직접 호출하는 대신 `.delay()`/`.apply_async()`로 enqueue한다.

## Rationale

1. SMTP 지연과 가입 API 응답 시간을 분리해서, 메일 서버 상태가 가입 API 성능에 영향을 주지 않게 한다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓸 수 있어서 추가 인프라 운영 부담이 없다.

## Alternatives

### RQ (Redis Queue)

- **Pros:** Python 작업 큐로서 구성이 단순하다.
- **Cons:** 브로커로 Redis가 필요하다.
- **Rejected because:** 현재 Redis를 운영하지 않아서, RQ를 쓰려면 Redis를 새로 도입하고 운영해야 한다.
- **Recheck if:** 다른 목적으로 Redis를 운영하게 되거나, RabbitMQ 운영을 중단·교체하게 될 때

## Consequences

### Positive

- SMTP가 느리거나 장애가 나도 가입 API 응답 시간이 유지된다.
- 발송 실패를 워커의 재시도로 처리할 수 있다.

### Negative

- Celery 워커 프로세스를 추가로 배포하고 운영해야 한다.
- 가입 API 응답 시점에 메일 발송 성공 여부를 알 수 없고, 사용자가 메일을 받기까지 지연이 생길 수 있다.

### Risks

- RabbitMQ 장애 시 enqueue가 실패하면 가입 API가 에러를 반환할 수 있다. enqueue 실패를 어떻게 처리할지 정해야 한다.
- 워커가 다운되거나 큐가 쌓이면 인증 메일이 늦어지는데, 이는 API 지표로는 보이지 않는다.
- 재시도나 at-least-once 전달 때문에 인증 메일이 중복 발송될 수 있다.
- 현재 SMTP 호출에 timeout이 없어서, 워커로 옮긴 뒤에도 SMTP가 멈추면 워커 슬롯을 계속 점유한다. 이관할 때 timeout을 지정해야 한다.

## Implementation

- [x] `pyproject.toml`에 `celery>=5.4` 추가
- [ ] 구현 작업: Celery 앱 설정(브로커 URL=RabbitMQ), `send_verification` task 전환(SMTP timeout·재시도 설정 포함), 가입 처리 코드를 enqueue 호출로 변경
- [ ] 테스트: task 단위 테스트(eager 모드), 가입 API가 SMTP 지연과 무관하게 응답하는지 확인
- [ ] 모니터링: 큐 적체량, task 실패·재시도 수, 워커 생존 여부
- [ ] 문서/설정 업데이트: 워커 실행 방법, 브로커 접속 설정(환경변수) 문서화

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리 코드의 enqueue 호출을 기존 동기 `send_verification()` 직접 호출로 되돌린다. 워커를 중지하고 `pyproject.toml`에서 `celery`를 제거한다. 브로커는 기존 RabbitMQ라서 따로 정리할 인프라가 없다.
- **Migration Cost:** Low

## Review Trigger

- 다른 목적으로 Redis를 운영하게 되거나, RabbitMQ 운영을 중단·교체하게 될 때 (RQ 재검토)

## References

- **Documentation:** `pyproject.toml` 의존성 변경(커밋 전), 기존 동기 발송 구현 `app/mail.py` (커밋 4304a04)
