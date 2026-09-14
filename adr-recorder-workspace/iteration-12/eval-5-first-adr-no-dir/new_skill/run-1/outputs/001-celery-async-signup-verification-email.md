# ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업으로 분리해 RabbitMQ 브로커를 통해 비동기 발송한다.
- **Scope:** signup-api / 회원가입 인증 메일 발송
- **Decision Source:** Human

---

## Context <!-- 필수 -->

### Problem

`app/mail.py`의 `send_verification()`이 가입 요청 처리 흐름 안에서 `smtplib.SMTP("smtp.internal", 25)`로 메일을 동기 발송한다(최초 구현: 커밋 8014104). 이 때문에 SMTP 서버가 느려지면 그 지연이 그대로 가입 API 응답 시간으로 전파된다. 메일 발송은 가입 성공 여부를 좌우하는 작업이 아닌데도 API 응답 지연의 원인이 되고 있다.

### Constraints

- 브로커는 이미 운영 중인 RabbitMQ를 사용한다. 이번 결정으로 새로 운영해야 하는 인프라는 없어야 한다.
- 런타임은 Python >=3.11, 웹 프레임워크는 FastAPI다.

## Decision <!-- 필수 -->

### Selected

- **Technology:** Celery >= 5.4 (`pyproject.toml` 의존성에 추가됨)
- **Architecture:** 가입 API는 인증 메일 발송을 Celery 작업으로 큐에 넣고 즉시 응답한다. 브로커는 기존 운영 중인 RabbitMQ를 사용하고, 실제 SMTP 발송은 별도 Celery 워커 프로세스가 수행한다.
- **Implementation:** `app/mail.py`의 동기 발송 로직을 Celery 태스크로 옮기고, 가입 요청 처리 경로에서는 직접 호출 대신 태스크를 큐에 넣는 호출로 교체한다.

## Rationale <!-- 필수 -->

1. 메일 발송을 요청 처리 경로 밖으로 빼면 SMTP 지연이 가입 API 응답 시간에 영향을 주지 않는다.
2. 브로커로 이미 운영 중인 RabbitMQ를 쓰므로 신규 인프라 운영 부담 없이 도입할 수 있다.
3. Celery는 RabbitMQ를 브로커로 바로 지원하며, 재시도 등 발송 실패 처리를 작업 큐 계층에서 다룰 수 있다.

## Alternatives <!-- 발견 가능한 경우만 -->

### RQ

- **Pros:** 파이썬 작업 큐로 Celery보다 단순한 구성.
- **Cons:** 브로커로 Redis가 필요한데 현재 운영 중인 Redis가 없다.
- **Rejected because:** Redis를 새로 운영해야 해서 제외했다.

### 현행 유지 (요청 처리 중 동기 발송)

- **Pros:** 추가 컴포넌트(워커·브로커 연동) 없이 현재 코드 그대로 동작한다.
- **Cons:** SMTP가 느릴 때 가입 API 응답까지 같이 느려진다.
- **Rejected because:** 그 지연 전파가 이번에 해결하려는 문제 자체다.

## Consequences <!-- 필수 -->

### Positive

- 가입 API 응답 시간이 SMTP 응답 속도와 분리된다.
- 메일 발송 실패를 작업 큐 수준에서 재시도로 다룰 수 있다.

### Negative

- Celery 워커 프로세스가 배포·모니터링 대상으로 추가된다.
- 메일 발송이 API 응답 이후에 일어나므로, 발송 결과를 가입 응답에서 즉시 알 수 없다.

### Risks

- 워커가 죽거나 큐가 밀리면 인증 메일이 지연되어 가입 완료까지의 사용자 경험이 나빠진다.
- 브로커(RabbitMQ) 장애가 이제 가입 플로우의 인증 메일 단계에 영향을 준다.
- 워커에서 발송이 실패할 경우 사용자에게 드러나지 않으므로 별도 관측 수단이 없으면 놓칠 수 있다.

## Implementation <!-- 구현 결정일 때만 -->

- [ ] `app/mail.py`의 발송 로직을 Celery 태스크로 전환하고 가입 경로를 큐 적재 호출로 교체
- [ ] Celery 앱 설정(RabbitMQ 브로커 URL) 추가 및 워커 실행 구성
- [ ] 태스크 단위 테스트 및 가입 API가 SMTP 지연에 영향받지 않는지 확인
- [ ] 큐 적체·태스크 실패율 모니터링
- [ ] 배포 문서에 워커 프로세스 실행 방법 반영

## Reversibility <!-- 가능하면 항상 -->

- **Reversible:** Yes
- **Rollback:** 가입 경로를 `app/mail.py`의 동기 `send_verification()` 직접 호출로 되돌리고 `pyproject.toml`에서 `celery>=5.4`를 제거한다. 동기 발송 코드는 커밋 8014104 시점 형태로 남아 있고, 현재 작업 트리는 HEAD(f8ac775) 기준으로 `pyproject.toml`만 변경된 상태다.
- **Migration Cost:** Low

## References <!-- PR/Issue/Related ADR/근거 문서 중 하나라도 있을 때만 -->

- **Documentation:**
  - 동기 발송 구현이 실제로 포함된 커밋: 8014104 (`app/mail.py`, `pyproject.toml`) — 메시지상 관련돼 보이는 f8ac775는 파일 변경이 없는 빈 커밋이라 근거로 인용하지 않았다.
  - 변경 대상 파일: `app/mail.py`, `pyproject.toml`
