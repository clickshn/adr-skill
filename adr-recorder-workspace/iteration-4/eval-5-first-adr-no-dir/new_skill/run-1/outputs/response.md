ADR을 작성했습니다: `docs/adr/001-async-verification-mail-with-celery.md`

저장소에 `docs/adr/` 디렉터리가 없어서 새로 만들고 첫 번호인 **001**부터 시작했습니다.

**요약**
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일(`app/mail.py`의 `send_verification()`)을 Celery 작업(브로커: 기존 RabbitMQ)으로 분리
- **Decision Source:** Human (말씀하신 결정을 기록한 것이라 Confidence 필드는 생략)
- **Context:** SMTP 지연이 가입 API 응답 지연으로 이어지는 문제. 제약은 기존 RabbitMQ를 쓰고 새 인프라를 늘리지 않는 것
- **Alternatives:** RQ. Redis를 새로 운영해야 해서 기각했고, Review Trigger는 "다른 용도로 Redis를 운영하게 될 때"로 적었습니다.
- **Consequences / Risks:** 워커 운영 부담이 늘고, API 성공과 실제 메일 발송이 분리됩니다. 워커나 브로커가 멈추면 메일이 쌓이거나 유실될 수 있고, 재시도하면 같은 메일이 중복 발송될 수 있습니다.
- **Reversibility:** Yes / Low. 4304a04 시점의 동기 호출로 되돌리고, 워커를 내리고, `celery` 의존성을 제거하면 됩니다.
- **References:** 4304a04, `app/mail.py`, `pyproject.toml`의 `celery>=5.4` 추가(아직 커밋 전)

측정 수치(SMTP 지연 시간, 가입 API p95 등)는 대화에 없어서 Evidence 섹션은 만들지 않았습니다. 수치가 있으면 추가할 수 있습니다. 아직 구현 전이라 Status는 **Proposed**로 두었고, 적용한 뒤에 Accepted로 바꾸시면 됩니다. `docs/adr/` 밖의 파일은 수정하지 않았습니다.
