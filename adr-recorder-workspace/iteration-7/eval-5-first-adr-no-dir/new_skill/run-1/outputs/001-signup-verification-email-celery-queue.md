# ADR-001: 가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 회원가입 인증 메일을 요청 처리 중 동기 발송하던 방식에서, 기존 RabbitMQ를 브로커로 쓰는 Celery 작업 큐 발송으로 전환한다.
- **Scope:** signup-api / 가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

가입 API가 요청 처리 중에 `send_verification()`으로 SMTP 발송을 동기로 수행한다. 그래서 SMTP 서버가 느려지면 가입 API 응답도 같이 느려진다. 현재 코드의 `smtplib.SMTP("smtp.internal", 25)` 호출에는 타임아웃 인자가 없어서, SMTP 지연이 요청 스레드에 그대로 전파된다.

### Constraints

- 브로커는 이미 운영 중인 RabbitMQ를 사용한다. 새 인프라 운영 부담은 늘리지 않는다.
- Python >= 3.11, FastAPI 기반 서비스 (`pyproject.toml`)

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`), 브로커는 기존 RabbitMQ
- **Architecture:** 가입 API는 메일 발송 작업을 큐에 넣기만 하고 즉시 응답한다. 실제 SMTP 발송은 별도 Celery 워커가 처리한다.
- **Implementation:** `pyproject.toml` 의존성에 `celery>=5.4`를 추가했다. `app/mail.py`의 `send_verification`은 아직 동기 발송 상태이며, 이를 Celery 작업으로 바꿔 가입 흐름에서 비동기로 호출하도록 전환한다.

## Rationale

1. SMTP 발송을 요청 경로에서 분리해 SMTP 지연이 가입 API 응답 시간에 영향을 주지 않게 한다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓸 수 있어 새 인프라가 필요 없다.

## Alternatives

### RQ (Redis Queue)

- **Cons:** 브로커로 Redis가 필요하다.
- **Rejected because:** Redis를 새로 운영해야 한다. 이미 운영 중인 RabbitMQ를 활용할 수 있는 Celery를 택했다.

### 현행 유지 (요청 처리 중 동기 발송)

- **Pros:** 워커나 브로커 연동이 필요 없어 단순하다. 발송 실패를 가입 요청 처리 중에 바로 알 수 있다.
- **Cons:** SMTP 지연이 가입 API 지연으로 직결된다.
- **Rejected because:** SMTP가 느릴 때 가입 API까지 같이 느려진다.

## Consequences

### Positive

- SMTP 지연이나 장애가 가입 API 응답 시간에서 분리된다.
- 새 인프라 없이 기존 RabbitMQ로 비동기 처리 기반을 확보한다.

### Negative

- Celery 워커 프로세스를 새로 배포하고 운영해야 한다.
- 메일 발송 결과가 가입 응답 시점에 확정되지 않는다. 발송 실패는 워커 쪽에서 따로 처리해야 한다.

### Risks

- 워커가 멈추거나 큐가 적체되면 인증 메일이 늦게 가고, 인증 토큰 유효기간 안에 도착하지 못할 수 있다.
- 재시도 정책이 없으면 일시적인 SMTP 오류에 메일이 유실될 수 있다.
- 가입 API의 가용성이 RabbitMQ 가용성에 새로 의존하게 된다(작업을 넣을 때 브로커에 연결할 수 있어야 함).

## Implementation

- [ ] Celery 앱 구성 (RabbitMQ 브로커 URL 설정)
- [ ] `send_verification`을 Celery 작업으로 전환하고 가입 흐름에서 `.delay()`/`apply_async()`로 호출
- [ ] SMTP 오류 재시도 정책과 SMTP 타임아웃 설정
- [ ] 테스트 (작업 등록, 워커 발송, 실패/재시도 경로)
- [ ] 모니터링 (큐 적체, 작업 실패율, 워커 상태)
- [ ] 워커 배포 설정과 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 흐름의 작업 큐 호출을 기존 동기 `send_verification()` 호출로 되돌리고, `pyproject.toml`에서 `celery`를 뺀 뒤 워커를 내린다. 전환 시점에 큐에 남은 작업은 먼저 비워야 한다.
- **Migration Cost:** Low

## References

- **Documentation:** 동기 발송 구현 커밋 `c44bbf9` (feat: 가입 인증 메일 발송). 의존성 추가는 `pyproject.toml` 작업 트리 변경(`celery>=5.4`, 미커밋)
