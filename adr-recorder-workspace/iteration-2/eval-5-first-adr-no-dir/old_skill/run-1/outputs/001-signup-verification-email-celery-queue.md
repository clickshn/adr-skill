# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 분리

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업 큐(브로커: 기존 RabbitMQ)로 비동기 발송한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송
- **Decision Source:** Human

---

## Context

### Problem

회원가입 인증 메일을 가입 API 요청 처리 흐름 안에서 동기로 SMTP 발송하고 있어, SMTP 서버 응답이 느릴 때 가입 API 응답까지 함께 느려진다.

### Constraints

- 메시지 브로커는 이미 운영 중인 RabbitMQ를 재사용한다 (신규 인프라 운영 부담 회피).
- 기존 스택: Python >=3.11, FastAPI, SQLAlchemy.

## Decision

### Selected

- **Technology:** Celery (`celery>=5.4`), 브로커 RabbitMQ (기존 운영 중)
- **Architecture:** 가입 API는 인증 메일 발송 작업을 큐에 넣고 바로 응답하고, 별도 Celery 워커가 큐에서 작업을 꺼내 SMTP 발송을 수행한다.
- **Implementation:** `pyproject.toml` 의존성에 `celery>=5.4` 추가 완료. 인증 메일 발송 로직을 Celery task로 옮기고 가입 API에서는 task enqueue만 수행한다.

## Rationale

1. SMTP 지연을 가입 API 요청 경로에서 분리해 가입 응답 시간이 메일 서버 상태에 좌우되지 않게 한다.
2. 이미 운영 중인 RabbitMQ를 브로커로 쓸 수 있어 새 인프라를 추가하지 않아도 된다.
3. RQ는 Redis를 새로 운영해야 해서 제외했고, Celery는 RabbitMQ를 브로커로 쓸 수 있다.

## Alternatives

### RQ (Redis Queue)

- **Cons:** 브로커로 Redis가 필요하며, 현재 운영 인프라에 Redis가 없다.
- **Rejected because:** Redis를 새로 도입·운영해야 하는 부담 때문에 제외 (이미 운영 중인 RabbitMQ를 활용할 수 없음).
- **Recheck if:** 다른 용도로 Redis가 운영 인프라에 도입되는 경우.

## Consequences

### Positive

- 가입 API 응답 시간이 SMTP 지연과 분리된다.
- 메일 발송을 별도 워커에서 처리하므로 발송 부하·실패가 API 프로세스에 직접 영향을 주지 않는다.

### Negative

- Celery 워커 프로세스를 추가로 배포·운영해야 한다.
- 가입 API 응답 시점에는 메일 발송 성공 여부를 알 수 없다 (발송 결과가 비동기로 결정됨).

### Risks

- 워커 장애나 큐 적체 시 인증 메일이 지연되거나 유실되어 사용자가 가입 인증을 완료하지 못할 수 있다.
- 작업 재시도 시 인증 메일이 중복 발송될 수 있다.
- RabbitMQ 장애가 가입 흐름(작업 enqueue)에 영향을 줄 수 있다.

## Implementation

- [x] `pyproject.toml`에 `celery>=5.4` 추가
- [ ] 인증 메일 발송 로직을 Celery task로 분리하고 가입 API에서 동기 발송을 enqueue로 교체
- [ ] Celery 앱의 RabbitMQ 브로커 연결 설정
- [ ] 테스트: 발송 task 단위 테스트, 가입 API가 SMTP 호출 없이 응답하는지 검증
- [ ] 모니터링: 큐 길이, 워커 상태, 발송 실패·재시도 건수
- [ ] 문서/설정 업데이트: 워커 실행·배포 설정

## Reversibility

- **Reversible:** Yes
- **Rollback:** 가입 API의 task enqueue 호출을 기존 동기 발송 함수 호출로 되돌리고 워커를 내린다.
- **Migration Cost:** Low

## Review Trigger

- 다른 용도로 Redis가 운영 인프라에 도입되는 경우 (RQ 재검토)

## References

- **Documentation:** 기존 동기 발송 도입 커밋 `9ef6bd8` (feat: 가입 인증 메일 발송), 의존성 변경 `pyproject.toml` (`celery>=5.4`)
