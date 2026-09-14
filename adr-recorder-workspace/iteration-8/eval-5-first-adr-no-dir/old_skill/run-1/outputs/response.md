ADR을 남겼습니다: `docs/adr/001-signup-verification-mail-celery-queue.md`

프로젝트에 `docs/adr/` 디렉터리가 없어서 새로 만들고 **ADR-001**부터 시작했습니다.

**주요 내용**
- **Status:** Proposed. 새로 내리는 결정이라, `pyproject.toml`에 celery가 이미 들어가 있어도 Proposed로 시작합니다.
- **Decision:** 가입 요청 처리 중 동기로 보내던 인증 메일을 Celery 작업(브로커: 운영 중인 RabbitMQ)으로 분리
- **Context:** SMTP가 느릴 때 가입 API까지 느려지는 문제. 현재 `app/mail.py`의 `send_verification()`이 `smtplib.SMTP("smtp.internal", 25)`를 timeout 없이 동기 호출하고 있다는 점도 한 줄 적었습니다.
- **Alternatives:** RQ. Redis를 새로 운영해야 해서 기각했습니다. Review Trigger는 "다른 이유로 Redis를 운영하게 되는 경우"입니다.
- **Consequences:** 워커 운영 부담, 발송 완료가 보장되지 않는 점, 워커 중단이나 RabbitMQ 장애 시의 적체·enqueue 실패, 재시도로 인한 중복 발송 위험을 적었습니다.
- **Implementation:** celery 의존성 추가는 완료로 체크했고, 태스크 전환·호출부 교체·테스트·모니터링·워커 설정은 남은 작업으로 두었습니다.
- **Reversibility:** Yes / Low. 기존 `send_verification()` 동기 호출로 되돌리고, 큐를 소진한 뒤 워커를 내리고 celery를 제거하면 됩니다.
- **References:** 동기 발송을 도입한 커밋 `c44bbf9`를 연결했습니다.

실측 수치가 없어서 Evidence 섹션은 만들지 않았습니다. `docs/adr/` 밖의 파일은 수정하지 않았습니다.
