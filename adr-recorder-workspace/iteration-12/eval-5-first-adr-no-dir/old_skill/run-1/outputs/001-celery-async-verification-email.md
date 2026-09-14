# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기 처리

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업 큐(브로커: 기존 RabbitMQ)로 분리해 비동기 발송한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/mail.py`의 `send_verification()`은 가입 요청 처리 흐름 안에서 `smtplib.SMTP`로 메일을 동기 발송한다. SMTP 서버(`smtp.internal`)가 느려지면 그 지연이 그대로 가입 API 응답 시간에 전가되어, 메일 인프라의 상태가 가입 API의 가용성·응답성을 좌우한다.

### Constraints

- 브로커를 새로 도입하지 않고 이미 운영 중인 RabbitMQ를 재사용해야 한다(신규 인프라 운영 부담 회피).
- 런타임은 Python 3.11+, 웹 프레임워크는 FastAPI.

## Decision

### Selected

- **Technology:** Celery 5.4+ (`pyproject.toml` dependencies에 `celery>=5.4` 추가됨)
- **Architecture:** 가입 API는 인증 메일 발송을 Celery 태스크로 큐에 넣고 즉시 응답한다. 실제 SMTP 발송은 별도 워커 프로세스가 수행한다. 메시지 브로커는 기존 운영 중인 RabbitMQ를 사용한다.
- **Implementation:** `send_verification()`의 SMTP 발송 로직을 Celery 태스크로 옮기고, 가입 요청 처리 경로에서는 태스크 호출(enqueue)만 수행하도록 변경한다.

## Rationale

1. SMTP 지연이 가입 API 응답 시간에 전파되는 결합을 끊는다. 메일 발송은 가입 요청의 성공 여부를 결정할 필요가 없는 작업이다.
2. 브로커로 이미 운영 중인 RabbitMQ를 쓰므로 새로 운영해야 할 인프라가 없다.
3. Celery는 RabbitMQ를 브로커로 표준 지원하며, 재시도·워커 분리 등 발송 실패 처리를 큐 계층에서 다룰 수 있다.

## Alternatives

### RQ (Redis Queue)

- **Pros:** Python 작업 큐로 Celery보다 단순하다.
- **Cons:** 브로커로 Redis가 필요하다.
- **Rejected because:** Redis를 새로 운영해야 해서. 이미 RabbitMQ가 운영 중인 상황에서 브로커 인프라가 하나 더 늘어난다.

### 현행 유지 (요청 처리 중 동기 발송)

- **Pros:** 추가 의존성·워커 프로세스가 없고, 발송 결과를 요청 처리 안에서 바로 확인할 수 있다.
- **Cons:** SMTP가 느릴 때 가입 API 응답까지 함께 느려진다.
- **Rejected because:** 이 결합이 곧 이번 변경의 동기다.

## Consequences

### Positive

- 가입 API 응답 시간이 SMTP 응답 속도와 분리된다.
- 발송 실패 시 재시도를 워커 쪽에서 처리할 여지가 생긴다.

### Negative

- Celery 워커라는 배포·운영 대상이 하나 늘어난다(프로세스 기동, 모니터링, 배포 파이프라인).
- 메일 발송이 요청 처리 밖으로 나가므로, 발송 실패가 가입 응답에 즉시 드러나지 않는다.

### Risks

- 워커가 죽거나 밀리면 인증 메일이 지연되고, 사용자는 가입은 됐으나 인증 링크를 못 받는 상태에 놓인다.
- 큐 적체나 발송 실패를 관측할 수단이 없으면 장애가 조용히 누적될 수 있다.

## Implementation

- [ ] `app/mail.py`의 SMTP 발송 로직을 Celery 태스크로 분리하고, 가입 요청 경로는 enqueue만 수행하도록 변경
- [ ] Celery 앱 설정(RabbitMQ 브로커 URL) 추가 및 워커 실행 구성
- [ ] 태스크 enqueue / 발송 경로 테스트
- [ ] 큐 적체·태스크 실패율 모니터링
- [ ] 워커 배포·실행 방법 문서화

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 요청 경로에서 태스크 enqueue 대신 `send_verification()`을 직접 호출하도록 되돌리고(동기 발송 구현은 커밋 8014104의 `app/mail.py` 형태), `pyproject.toml`에서 `celery` 의존성과 워커 배포 구성을 제거한다. 기존 RabbitMQ는 다른 용도로 계속 운영되므로 브로커 철거는 필요 없다.
- **Migration Cost:** Low

## References

- **Documentation:** `app/mail.py` (현행 동기 발송 구현), `pyproject.toml` (`celery>=5.4` 추가). 동기 발송 구현이 실제로 들어온 커밋은 8014104이다(커밋 f8ac775는 "feat: 가입 인증 메일 발송" 메시지를 달고 있으나 변경 파일이 없는 빈 커밋이라 근거로 인용하지 않는다).
