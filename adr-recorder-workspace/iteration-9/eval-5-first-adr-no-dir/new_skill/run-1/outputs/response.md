ADR을 작성했습니다: `docs/adr/001-signup-verification-mail-celery.md`

프로젝트에 `docs/adr/` 디렉터리가 없어서 새로 만들고, 첫 ADR인 **001**로 시작했습니다.

**요약**
- **Status:** Proposed (새로 내리는 결정이라 Proposed로 시작합니다. `pyproject.toml`에는 celery가 추가돼 있지만 `app/mail.py`는 아직 동기 발송입니다)
- **Decision:** 가입 인증 메일 발송을 Celery 작업으로 분리하고, 브로커는 이미 운영 중인 RabbitMQ를 씁니다
- **Decision Source:** Human
- **Alternatives:**
  - RQ: Redis를 새로 운영해야 해서 기각. Recheck if는 "Redis를 운영하게 되는 경우"로 적었고, 이 조건을 Review Trigger에도 올렸습니다.
  - 현행 유지(동기 발송): SMTP가 느리면 가입 API도 느려져서 기각.
- **Reversibility:** Yes / Low. 되돌릴 때는 동기 호출로 복귀하고, 워커를 내리기 전에 큐에 남은 작업을 먼저 소진합니다.

**참고**
- 현재 `app/mail.py`의 `smtplib.SMTP(...)` 호출에는 timeout이 없습니다. 그래서 SMTP가 지연되면 그 시간이 요청 처리 시간에 그대로 더해집니다. 이 내용은 Context > Problem에 한 줄로 적었습니다.
- 측정 수치가 없어서 Evidence 섹션은 만들지 않았습니다.
