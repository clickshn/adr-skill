ADR을 남겼습니다: `docs/adr/001-verification-email-celery-queue.md`

저장소에 `docs/adr/` 디렉터리가 없어서 새로 만들고 **ADR-001**부터 번호를 매겼습니다.

**기록한 내용**
- **결정:** 회원가입 인증 메일 발송을 요청 처리 흐름에서 떼어내 Celery 작업 큐로 옮김. 브로커는 이미 운영 중인 RabbitMQ
- **Status:** Proposed. 새로 내린 결정이라 `pyproject.toml`에 이미 celery가 추가돼 있어도 Proposed로 시작합니다.
- **배경:** SMTP가 느려지면 가입 API도 같이 느려짐. 현재 `app/mail.py`의 `send_verification()`은 `smtplib.SMTP("smtp.internal", 25)`에 타임아웃 없이 동기로 연결합니다.
- **대안:** RQ. Redis를 새로 운영해야 해서 기각했다고 적었습니다. Review Trigger는 "다른 이유로 Redis를 운영하게 되는 경우"입니다.
- **구현 체크리스트:** 코드에는 아직 의존성 추가만 반영돼 있어서 남은 작업을 체크리스트로 적었습니다. `send_verification`을 Celery task로 전환, SMTP 실패 시 재시도 정책, 큐 적체와 워커 모니터링, 워커 배포 설정입니다.
- **Reversibility:** 되돌릴 수 있고(Yes) 비용도 낮음(Low). 동기 호출로 돌리고 celery 의존성을 제거하면 됩니다.

실측 수치(예: SMTP 지연 시 가입 API 응답 시간)가 없어서 Evidence 섹션은 넣지 않았습니다. 수치가 있으면 알려주세요. 추가하겠습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.
