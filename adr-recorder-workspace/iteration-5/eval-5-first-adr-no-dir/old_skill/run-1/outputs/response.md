ADR을 남겼습니다: `docs/adr/001-async-verification-email-with-celery.md`

- 저장소에 `docs/adr/` 디렉터리가 없어서 새로 만들고 번호는 **001**부터 시작했습니다.
- **결정:** 가입 인증 메일을 동기 SMTP 발송에서 Celery 작업으로 옮기고, 브로커는 기존 운영 중인 RabbitMQ를 씁니다. `pyproject.toml`의 `celery>=5.4` 추가분도 반영했습니다.
- **Context:** SMTP가 느리면 가입 API도 같이 느려지는 문제를 적었습니다. 현재 `app/mail.py`의 SMTP 연결에 timeout이 없다는 점도 한 줄 넣었습니다.
- **Alternatives:** RQ는 Redis를 새로 운영해야 해서 기각했다고 적었습니다. 재검토 조건은 "Redis를 다른 이유로 운영하게 되거나, RabbitMQ 운영을 중단할 때"로 두었고, Review Trigger에도 같은 내용이 들어갑니다.
- **Evidence:** 측정 수치가 없어서 섹션을 만들지 않았습니다. SMTP 지연이 가입 API 응답 시간에 준 영향을 측정한 값(예: p95 응답 시간)이 있으면 알려주세요. 추가하겠습니다.
- **Status:** `Proposed`로 두었습니다. 지금 `app/mail.py`는 아직 동기 발송이라서, Implementation 섹션에 전환 작업 체크리스트를 넣었습니다. 전환을 마치면 `Accepted`로 바꾸시면 됩니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.
