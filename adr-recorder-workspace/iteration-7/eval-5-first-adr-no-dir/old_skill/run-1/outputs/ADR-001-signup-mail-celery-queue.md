# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업(브로커: 기존 RabbitMQ)으로 분리해 비동기 발송한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송 (`app/mail.py`)
- **Decision Source:** Human

---

## Context

### Problem

현재 `app/mail.py`의 `send_verification()`은 가입 요청 처리 흐름 안에서 `smtplib.SMTP("smtp.internal", 25)`로 인증 메일을 동기 발송한다. 그래서 SMTP 서버 응답이 느리면 가입 API 응답도 같이 느려진다.

### Constraints

- 메시지 브로커는 이미 운영 중인 RabbitMQ를 사용한다.
- 새 인프라(예: Redis)를 추가로 운영하지 않는다.
- Python >= 3.11, FastAPI 기반 서비스다(`pyproject.toml`).

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`, `pyproject.toml`에 추가됨), 브로커 RabbitMQ
- **Architecture:** 가입 API는 인증 메일 발송 작업을 큐에 넣고 바로 응답한다. SMTP 발송은 별도 Celery 워커가 맡는다.
- **Implementation:** `send_verification()`을 Celery 태스크로 바꾸고, 가입 처리 코드는 직접 호출하는 대신 태스크를 큐에 넣는다. 현재 커밋 기준으로 코드는 아직 동기 발송이고, 의존성만 추가된 상태다.

## Rationale

1. SMTP 발송을 요청 처리 경로에서 떼어내면 SMTP 지연이 가입 API 응답 시간에 번지지 않는다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓰므로 새 인프라를 운영할 필요가 없다.
3. Celery는 RabbitMQ를 브로커로 지원하므로 기존 인프라에 바로 붙일 수 있다.

## Alternatives

### 현행 유지 (요청 처리 중 동기 발송)

- **Pros:** 워커나 큐를 따로 구성하지 않아도 되어 단순하다.
- **Cons:** SMTP가 느리면 가입 API도 같이 느려진다.
- **Rejected because:** SMTP 지연이 가입 API 응답 지연으로 바로 이어지는 문제가 이번 결정의 출발점이다.
- **Recheck if:** SMTP 지연이 가입 API 응답에 영향을 주지 않을 만큼 안정되거나, 비동기 워커 운영 부담이 이 지연보다 커지는 경우

### RQ (Redis Queue)

- **Cons:** 브로커로 Redis가 필요해서 Redis를 새로 운영해야 한다.
- **Rejected because:** 현재 Redis를 운영하지 않아 새 인프라를 들여야 하고, 이미 운영 중인 RabbitMQ를 쓸 수 없다.
- **Recheck if:** 다른 목적으로 Redis를 운영하게 되는 경우

## Consequences

### Positive

- SMTP 지연이나 장애가 가입 API 응답 시간에 영향을 주지 않는다.
- 기존 RabbitMQ를 재사용하므로 새 인프라 없이 도입할 수 있다.

### Negative

- Celery 워커 프로세스를 따로 배포하고 운영해야 한다.
- 가입 API가 응답하는 시점에는 메일 발송 성공 여부를 알 수 없다. 발송이 요청 이후로 밀린다.

### Risks

- 워커가 멈추거나 RabbitMQ에 장애가 나면 인증 메일이 쌓이거나 늦어져서, 사용자가 인증을 완료하지 못할 수 있다.
- 발송 실패가 API 오류로 드러나지 않는다. 재시도와 실패 모니터링이 없으면 메일이 누락되어도 알아채기 어렵다.
- 인증 토큰이 태스크 인자로 브로커를 거쳐 전달된다.

## Implementation

- [x] `pyproject.toml`에 `celery>=5.4` 의존성 추가
- [ ] Celery 앱 구성 및 RabbitMQ 브로커 연결 설정
- [ ] `app/mail.py`의 `send_verification()`을 Celery 태스크로 바꾸고, 가입 처리에서 비동기로 호출하도록 변경
- [ ] 발송 실패 시 재시도 정책 설정
- [ ] 테스트: 가입 API가 SMTP 지연과 관계없이 응답하는지, 태스크가 메일을 실제로 보내는지 검증
- [ ] 모니터링: 큐 적체량, 태스크 실패율, 워커 상태
- [ ] 문서/설정 업데이트: 워커 실행 방법, 브로커 접속 설정

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 처리에서 태스크를 큐에 넣는 대신 `send_verification()`을 직접 호출(동기 발송)하도록 되돌리고, `pyproject.toml`에서 `celery`를 제거한다. 브로커는 기존 RabbitMQ라 따로 정리할 신규 인프라가 없다.
- **Migration Cost:** Low

## Review Trigger

- SMTP 지연이 가입 API 응답에 영향을 주지 않을 만큼 안정되거나, 비동기 워커 운영 부담이 이 지연보다 커지는 경우 (현행 동기 발송 재검토)
- 다른 목적으로 Redis를 운영하게 되는 경우 (RQ 재검토)

## References

- **Documentation:** 동기 발송을 도입한 커밋 `c44bbf9` (feat: 가입 인증 메일 발송), 의존성 변경은 `pyproject.toml` (아직 커밋 안 됨)
