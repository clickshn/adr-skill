ADR을 작성했습니다: `docs/adr/001-celery-async-verification-email.md`

- `docs/adr/` 디렉터리가 없어서(셸로 확인) 새로 만들고 **001번부터 시작**했습니다.
- **Status:** Proposed — 새로 내리는 결정이라 `pyproject.toml`에 celery가 이미 추가돼 있어도 Proposed로 시작합니다.
- **Decision Source:** Human (말씀하신 결정을 기록한 것이라 Confidence 필드는 생략)
- **Context:** SMTP가 느리면 가입 API도 같이 느려지는 문제. 저장소를 보니 `app/mail.py`의 `send_verification()`이 `smtp.internal:25`에 timeout 없이 동기로 접속하고 있어서 이 내용도 한 줄 넣었습니다.
- **Constraints:** 이미 운영 중인 RabbitMQ를 브로커로 쓰고, Redis 같은 새 인프라는 추가하지 않는다.
- **Alternatives:** 현행 유지(동기 발송)와 RQ 두 가지. 기각 사유는 말씀하신 대로(SMTP 지연이 API로 전파됨 / Redis를 새로 운영해야 함) 적었습니다.
- **Evidence** 섹션은 넣지 않았습니다. 실측 수치(SMTP 지연 시간, API 응답 시간 등)가 없어서입니다.
- **Recheck if / Review Trigger**도 넣지 않았습니다. 대화에 재검토 조건이 없었고, 지어내지 않았습니다.
- **References:** `app/mail.py`(커밋 751f118에서 도입)와 `pyproject.toml`의 미커밋 diff를 적었습니다. 최근 커밋 `286b20c feat: 가입 인증 메일 발송`은 `git show --stat`으로 보니 파일 변경이 없는 빈 커밋이라 인용하지 않았습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.
