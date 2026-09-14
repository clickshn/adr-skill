ADR을 남겼습니다: `docs/adr/001-verification-email-celery-queue.md`

저장소에 `docs/adr/` 디렉터리가 없어서 새로 만들고 첫 번호 **001**을 붙였습니다.

**ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 분리**
- **결정:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업으로 비동기 발송합니다. 브로커는 이미 운영 중인 RabbitMQ를 씁니다.
- **배경:** 지금 `app/mail.py`의 `send_verification()`이 요청 처리 중에 `smtp.internal:25`로 직접 보내고 있습니다. 그래서 SMTP가 느리면 가입 API도 같이 느려집니다.
- **대안 (RQ):** Redis를 새로 운영해야 해서 기각했습니다. 다시 볼 조건은 "다른 목적으로 Redis를 운영하게 될 때"로 적었고, 이 조건을 Review Trigger에도 넣었습니다.
- **Consequences:**
  - 좋은 점: 가입 API가 SMTP 지연에서 분리됩니다.
  - 대가: 워커를 따로 운영해야 합니다.
  - 리스크: 워커가 멈추면 메일이 큐에 쌓이고, 가입 API가 RabbitMQ에 의존하게 되며, 재시도하면 같은 메일이 두 번 갈 수 있습니다.
- **Reversibility:** 되돌릴 수 있습니다. 호출부를 다시 동기 호출로 바꾸고 celery 의존성을 빼면 되고, 워커를 내리기 전에 큐를 비워야 합니다. 비용은 Low로 봤습니다.
- **References:** 기존 동기 발송 커밋 `c5ffc58`과 `pyproject.toml` 변경(`celery>=5.4`)을 적었습니다.

참고할 점:
- 실측 수치(SMTP 지연 시간, 가입 API 응답 시간 등)가 없어서 Evidence 섹션은 넣지 않았습니다. 수치가 있으면 알려주세요, 추가하겠습니다.
- 아직 코드가 바뀌지 않아서 Status는 `Proposed`로 두었습니다. 적용이 끝나면 `Accepted`로 바꾸면 됩니다.
- 저장소에는 `send_verification()`을 호출하는 가입 처리 코드가 없어서, Implementation 체크리스트에 "호출부를 enqueue로 바꾸기"를 적어만 두었습니다.
