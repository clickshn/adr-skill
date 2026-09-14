인증 메일을 Celery로 비동기화하는 결정을 ADR로 남겼습니다. 결정 자체는 대화에서 알려주신 내용 그대로 옮겼고, 저장소에서 확인한 사항만 덧붙였습니다.

**파일:** `docs/adr/001-celery-async-verification-email.md` (Status: Proposed)

저장소에 `docs/adr/` 디렉터리가 없어서 새로 만들고 번호는 001부터 시작했습니다.

**ADR에 들어간 내용**
- **배경:** `app/mail.py`의 `send_verification()`이 가입 요청 처리 중에 `smtp.internal:25`로 메일을 동기 발송합니다. 그래서 SMTP가 느려지면 가입 API도 같이 느려집니다.
- **결정:** Celery(`celery>=5.4`, pyproject.toml에 추가된 것 확인)를 쓰고, 브로커는 이미 운영 중인 RabbitMQ를 재사용합니다.
- **대안:** RQ는 Redis를 새로 운영해야 해서 기각했습니다. Review Trigger에는 "Redis를 다른 목적으로 운영하게 되거나 RabbitMQ를 교체할 때 재검토"를 넣었습니다.
- **Decision Source:** 직접 내리신 결정이라 Human으로 적었고, 그래서 Confidence 필드는 생략했습니다. 실측 수치가 없어서 Evidence 섹션도 넣지 않았습니다.
- **되돌리기:** 가입 처리 코드를 동기 호출로 되돌리고 워커를 내리면 됩니다. 비용은 Low로 적었습니다.

**코드 확인 중 발견한 점**
현재 `smtplib.SMTP(...)` 호출에는 timeout이 없습니다. 워커로 옮긴 뒤에도 SMTP가 멈추면 워커 슬롯을 계속 잡고 있게 됩니다. 이관할 때 timeout과 재시도를 설정해야 한다고 Risks와 Implementation 체크리스트에 적어두었습니다.

pyproject.toml 변경은 아직 커밋 전이라 References에 커밋 해시 대신 "커밋 전"으로 적었습니다. PR을 만드시면 링크를 추가해 주세요.
