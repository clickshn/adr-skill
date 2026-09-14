ADR을 작성했습니다: `docs/adr/001-signup-verification-email-celery-queue.md`

프로젝트에 `docs/adr/` 디렉터리가 없어서(기존 ADR 없음) 새로 만들고 **001번부터** 시작했습니다.

**요약**
- **Status:** Proposed. 새로 내린 결정이라 `pyproject.toml`에 celery가 이미 추가돼 있어도 Proposed로 시작합니다.
- **Decision Source:** Human. 결정을 직접 말씀해 주셔서 Confidence 필드는 뺐습니다.
- **결정:** 가입 인증 메일 발송을 Celery 작업 큐로 옮기고, 브로커는 이미 운영 중인 RabbitMQ를 씁니다.
- **Alternatives:**
  - RQ: Redis를 새로 운영해야 해서 제외
  - 현행 유지(동기 발송): SMTP가 느리면 가입 API도 같이 느려져서 제외
- **Reversibility:** Yes / Low. 발송 로직이 지금은 `app/mail.py`의 `send_verification` 하나뿐이라 동기 호출로 되돌리기 쉽습니다.

**참고**
- `app/mail.py`는 아직 `smtplib`로 동기 발송하고 있습니다(커밋 286b20c). 그래서 Implementation 체크리스트에서는 celery 의존성 추가만 완료로 표시했습니다.
- 대화에 재검토 조건이 없어서 Recheck if와 Review Trigger는 넣지 않았습니다. 측정 수치도 없어서 Evidence 섹션은 만들지 않았습니다.
