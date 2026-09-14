ADR을 작성했습니다.

**`docs/adr/` 디렉터리가 없어서 이번 ADR을 첫 번째 기록인 001번으로 시작했습니다.** (디렉터리를 새로 만들었습니다.)

생성한 파일: `docs/adr/001-celery-async-verification-email.md`

정리한 내용:

- **Context** — `app/mail.py`의 `send_verification()`이 가입 요청 처리 흐름 안에서 `smtplib.SMTP`로 동기 발송 중이라, `smtp.internal`이 느려지면 그 지연이 가입 API 응답 시간으로 그대로 전가되는 상황.
- **Decision** — 발송을 Celery 태스크로 분리하고 브로커는 이미 운영 중인 RabbitMQ 재사용. `pyproject.toml`에 `celery>=5.4`가 추가된 것을 diff에서 확인했습니다.
- **Alternatives** — RQ(Redis를 새로 운영해야 해서 기각)와 현행 유지(동기 발송) 두 가지를 말씀하신 근거 그대로 적었습니다.
- **Status는 Proposed** 입니다. 의존성은 이미 추가되어 있지만, 기존 결정 로그를 옮긴 게 아니라 새로 내린 결정이라 Proposed로 시작합니다.

참고로 확인 중 발견한 점 하나: **커밋 `f8ac775` ("feat: 가입 인증 메일 발송")는 변경 파일이 없는 빈 커밋입니다.** 실제 `app/mail.py` 동기 발송 코드는 `8014104`("feat: signup-api 초기 구성")에 들어 있어서, References에는 `8014104`를 인용했습니다.

측정 수치가 없어서 Evidence 섹션은 만들지 않았고("SMTP가 느릴 때 가입 API도 느려진다"는 정성적 관찰이라 Context에 넣었습니다), 재검토 조건을 따로 말씀하신 게 없어서 Recheck if / Review Trigger도 생략했습니다. 만약 "Redis를 다른 용도로 이미 쓰게 되면 재검토" 같은 조건이 있으시면 알려주시면 추가하겠습니다.
