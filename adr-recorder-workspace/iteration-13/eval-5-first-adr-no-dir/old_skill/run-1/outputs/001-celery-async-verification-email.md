# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 분리

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업으로 빼고, 브로커는 기존 RabbitMQ를 사용한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/mail.py`의 `send_verification()`은 가입 요청 처리 중에 `smtplib.SMTP("smtp.internal", 25)`로 메일을 동기 발송한다. SMTP 서버가 느려지면 그 지연이 그대로 가입 API 응답 시간에 더해져, 메일 인프라의 문제가 가입 API의 문제로 번진다.

### Constraints

- 브로커를 새로 도입하지 않는다. 운영 중인 RabbitMQ를 재사용한다.
- 새 미들웨어를 운영 대상에 추가하면 그만큼 운영 부담이 늘어나므로, 신규 운영 컴포넌트를 요구하는 선택지는 배제한다.

## Decision

### Selected

- **Technology:** Celery 5.4 이상 (`pyproject.toml` 의존성에 `celery>=5.4` 추가됨)
- **Architecture:** 가입 API는 인증 메일 발송을 Celery 작업으로 큐잉하고 즉시 응답한다. 실제 SMTP 발송은 별도 워커 프로세스가 처리한다. 브로커는 기존 운영 중인 RabbitMQ.
- **Implementation:** `send_verification()`을 Celery task로 감싸고, 가입 처리 경로에서는 직접 호출 대신 작업 큐잉 호출로 교체한다. 워커 프로세스를 배포에 추가한다.

## Rationale

1. SMTP 지연을 가입 API 응답 경로 밖으로 밀어내, 메일 인프라 지연이 가입 API 지연으로 전파되지 않게 한다.
2. 브로커로 이미 운영 중인 RabbitMQ를 쓰므로 새로 운영해야 할 인프라가 없다.
3. Celery는 RabbitMQ를 브로커로 직접 지원해 별도 연결 계층 없이 붙일 수 있다.

## Alternatives

### RQ

- **Pros:** 구성이 단순한 파이썬 작업 큐.
- **Cons:** 브로커로 Redis를 요구해, 지금 없는 Redis를 새로 운영해야 한다.
- **Rejected because:** Redis를 신규로 운영해야 하는 부담 때문에 제외했다.

## Consequences

### Positive

- 가입 API 응답 시간이 SMTP 응답 시간과 분리된다.
- 메일 발송 재시도를 작업 큐 차원에서 다룰 수 있는 자리가 생긴다.

### Negative

- 워커 프로세스라는 배포·모니터링 대상이 하나 늘어난다.
- 메일 발송이 가입 응답 이후로 밀리므로, 발송 실패가 가입 요청의 응답으로 즉시 드러나지 않는다.

### Risks

- RabbitMQ 장애 시 인증 메일 발송이 중단된다. 기존에는 SMTP만 의존하던 경로에 브로커 의존이 추가된다.
- 큐가 밀리면 사용자가 인증 메일을 받기까지의 시간이 길어진다.

## Implementation

- [ ] `send_verification()`을 Celery task로 전환하고 가입 처리 경로를 큐잉 호출로 교체
- [ ] 작업 큐잉/발송 경로 테스트
- [ ] 워커·큐 적체 및 발송 실패 모니터링
- [ ] 브로커 연결 설정과 워커 배포 문서/설정 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리 경로를 `send_verification()` 직접 호출로 되돌리고 워커 배포와 `celery` 의존성을 제거한다. 되돌릴 기준 시점은 HEAD(558ed63)이며, 동기 발송 구현 원본은 ebfea45에 있다.
- **Migration Cost:** Low

## References

- **Documentation:** 동기 발송 구현 `app/mail.py` (커밋 ebfea45), 의존성 추가 `pyproject.toml` (`celery>=5.4`, 미커밋)
