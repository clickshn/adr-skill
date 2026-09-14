ADR을 만들었습니다: `docs/adr/001-celery-async-verification-email.md`

저장소에 `docs/adr/` 디렉터리 자체가 없어서 새로 만들고 **001번으로 시작**했습니다.

기록한 내용:

- **Status:** 새로 내리는 결정이라 `Proposed`로 두었습니다 (`pyproject.toml`에 celery가 이미 추가돼 있어도 마찬가지).
- **Context:** `app/mail.py`의 `send_verification()`이 가입 요청 처리 중에 `smtplib`로 동기 발송하고 있어, SMTP 지연이 가입 API 응답 시간에 그대로 더해지는 문제를 배경으로 적었습니다.
- **Decision:** 발송을 Celery 작업으로 큐잉하고 브로커는 운영 중인 RabbitMQ 재사용.
- **Alternatives:** RQ — Redis를 새로 운영해야 해서 기각.
- **Reversibility:** Yes / Migration Cost Low. 롤백 기준 시점은 HEAD(558ed63)로, 동기 발송 구현 원본은 ebfea45에 있습니다. (`558ed63`은 "feat: 가입 인증 메일 발송"이라는 메시지와 달리 파일 변경이 없는 빈 커밋이라, 구현 근거로는 실제로 `app/mail.py`를 담고 있는 `ebfea45`를 인용했습니다.)

측정 수치가 따로 없어서 Evidence 섹션은 만들지 않았고("SMTP가 느릴 때"는 정성적 관찰이라 Context로), 재검토 조건으로 말씀하신 게 없어서 Recheck if / Review Trigger도 비워두지 않고 생략했습니다. 재검토 기준(예: 큐 적체 시간, 메일 발송 실패율 임계치)이 있으면 알려주시면 채워 넣겠습니다.
