ADR을 생성했습니다: `docs/adr/001-signup-verification-email-celery-queue.md`

프로젝트에 `docs/adr/` 디렉터리가 없었습니다. 기존 ADR이 없어서 새로 만들고 첫 번호 **001**로 시작했습니다.

**요약**
- **제목:** ADR-001: 가입 인증 메일 발송을 Celery 작업 큐로 비동기화
- **Status:** Proposed (새 결정이라 제안 상태로 시작합니다. `pyproject.toml`에 celery가 이미 추가된 것과는 무관합니다.)
- **Date:** 2026-09-11
- **Decision Source:** Human (말씀하신 결정이라 Confidence 필드는 뺐습니다.)
- **Context:** SMTP 동기 발송 때문에 SMTP가 느리면 가입 API도 느려집니다. 기존 RabbitMQ를 쓰고 새 인프라는 늘리지 않는다는 제약도 적었습니다. 확인해 보니 `app/mail.py`의 `smtplib.SMTP("smtp.internal", 25)`에 타임아웃이 없어서, 이 내용도 Problem에 한 줄 적었습니다.
- **Alternatives:**
  - RQ: Redis를 새로 운영해야 해서 기각
  - 현행 동기 발송 유지: SMTP 지연이 가입 API 지연으로 이어져서 기각
- **Consequences/Risks:** 워커를 따로 운영해야 합니다. 발송 실패는 비동기로 처리해야 합니다. 큐가 밀리면 인증 메일이 늦을 수 있고, 가입 API가 RabbitMQ 가용성에 의존하게 됩니다.
- **Implementation:** 체크리스트를 넣었습니다. `app/mail.py`는 아직 동기 발송이라 Celery 작업 전환, 재시도, SMTP 타임아웃, 테스트, 모니터링 항목이 들어갔습니다.
- **Reversibility:** Yes / Low. 동기 호출로 되돌리고 celery 의존성을 빼면 됩니다. 되돌리기 전에 큐에 남은 작업을 먼저 비워야 합니다.
- **References:** 동기 발송 구현 커밋 `c44bbf9`, `pyproject.toml` 변경

**뺀 항목**
- Evidence: 측정 수치가 없어서 뺐습니다.
- Recheck if, Review Trigger: 대안을 다시 검토할 조건이 대화에 없어서 뺐습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.
