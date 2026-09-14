# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업으로 분리하고, 브로커는 기존 RabbitMQ를 사용한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

`app/mail.py`의 `send_verification()`은 가입 요청 처리 중에 `smtplib.SMTP("smtp.internal", 25)`로 인증 메일을 동기 발송한다. SMTP 응답이 느리면 가입 API 응답도 같이 느려진다.

### Constraints

- 메시지 브로커로 쓸 수 있는 RabbitMQ가 이미 운영 중이다.
- 작업 큐 때문에 새 인프라(예: Redis)를 추가로 운영하고 싶지 않다.
- 기존 스택: Python >=3.11, FastAPI, SQLAlchemy 2.x (`pyproject.toml`)

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, `pyproject.toml`에 추가됨) + RabbitMQ 브로커(기존 운영 인스턴스)
- **Architecture:** 가입 API는 인증 메일 발송 작업을 큐에 넣고 바로 응답한다. 실제 SMTP 발송은 별도 Celery 워커 프로세스가 맡는다.
- **Implementation:** `send_verification()`을 Celery task로 바꾸고, 가입 처리 경로에서는 직접 호출하는 대신 `.delay()`/`.apply_async()`로 작업만 넣는다.

## Rationale

1. SMTP 발송을 요청 경로에서 빼면 SMTP 지연이 가입 API 응답 시간에 영향을 주지 않는다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓰므로 인프라를 새로 늘리지 않아도 된다.
3. RabbitMQ를 브로커로 공식 지원하는 Celery를 쓰면 기존 인프라에 바로 붙일 수 있다.

## Alternatives

### RQ (Redis Queue)

- **Pros:** Python 작업 큐로 쓸 수 있고 비동기 발송이라는 목적을 똑같이 달성한다.
- **Cons:** Redis를 브로커로 써야 한다.
- **Rejected because:** Redis를 새로 운영해야 한다. 이미 운영 중인 RabbitMQ를 쓸 수 있는 Celery를 택했다.
- **Recheck if:** Redis를 다른 목적으로 운영하게 되어 추가 운영 부담이 사라지는 경우

## Consequences

### Positive

- SMTP가 느려도 가입 API의 응답 시간은 영향을 받지 않는다.
- 이후 다른 비동기 작업(알림 등)도 같은 Celery/RabbitMQ 구성에 올릴 수 있다.

### Negative

- Celery 워커 프로세스를 추가로 배포하고 운영해야 한다.
- 가입 API 응답 시점에는 메일이 실제로 발송됐는지 알 수 없다. 발송 실패는 API 응답이 아니라 워커 쪽에서 드러난다.

### Risks

- 워커가 멈추거나 밀리면 인증 메일이 늦게 가거나 가지 않을 수 있다. 큐 적체와 작업 실패 모니터링이 필요하다.
- SMTP 실패 시 재시도 정책이 없으면 메일이 유실되고, 재시도 설정에 따라서는 중복 발송될 수 있다.
- 인증 토큰이 작업 인자로 브로커(RabbitMQ)에 저장된다.
- 운영 중인 RabbitMQ를 다른 워크로드와 공유하므로 서로 부하에 영향을 줄 수 있다.

## Implementation

- [ ] Celery 앱 설정 추가 (`broker_url`를 기존 RabbitMQ로 지정)
- [ ] `app/mail.py`의 `send_verification()`을 Celery task로 전환하고 SMTP 실패 재시도 정책 설정
- [ ] 가입 처리 경로의 동기 호출을 `.delay()`/`.apply_async()` 호출로 교체
- [ ] Celery 워커 배포 구성 추가
- [ ] 테스트: task 등록·호출 단위 테스트, 가입 API가 SMTP 지연과 무관하게 응답하는지 확인
- [ ] 모니터링: 큐 길이, 작업 실패/재시도 건수
- [ ] 문서/설정 업데이트 (브로커 접속 정보, 워커 실행 방법)

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리 경로를 `send_verification()` 동기 직접 호출로 되돌리고, `pyproject.toml`에서 `celery`를 제거한 뒤 워커를 내린다. RabbitMQ는 기존 인프라라 따로 철거할 것이 없다. 되돌리기 전에 큐에 남은 작업은 모두 처리한다.
- **Migration Cost:** Low

## Review Trigger

- Redis를 다른 목적으로 운영하게 되어 추가 운영 부담이 사라지는 경우 (RQ 재검토)

## References

- **Documentation:** `app/mail.py` (현재 동기 발송 구현, 커밋 `1c47568`), `pyproject.toml` (`celery>=5.4` 추가, 미커밋 변경)
