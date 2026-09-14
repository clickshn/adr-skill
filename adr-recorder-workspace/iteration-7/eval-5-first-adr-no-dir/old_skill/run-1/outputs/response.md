ADR을 남겼습니다. `docs/adr/ADR-001-signup-mail-celery-queue.md`

프로젝트에 `docs/adr/` 디렉터리가 아직 없었습니다. 그래서 따로 여쭤보지 않고 디렉터리를 만들어 **001번부터** 시작했습니다.

**핵심 내용**
- **Status:** Proposed. `pyproject.toml`에 celery가 이미 추가돼 있지만 새로 내리는 결정이라 제안 상태로 시작합니다.
- **Decision Source:** 직접 내리신 결정이라 Human으로 적었고, 그래서 Confidence 필드는 뺐습니다.
- **Context:** 지금은 `app/mail.py`의 `send_verification()`이 가입 요청 처리 중에 `smtp.internal:25`로 메일을 동기 발송합니다. 그래서 SMTP가 느리면 가입 API도 같이 느려집니다. 브로커는 기존 RabbitMQ를 쓰고, 새 인프라는 늘리지 않는다는 제약도 적었습니다.
- **Alternatives:** 대화에 나온 대안 두 가지만 적었습니다.
  - 현행 동기 발송 유지: SMTP 지연이 가입 API로 그대로 번지는 문제 때문에 기각
  - RQ: Redis를 새로 운영해야 해서 기각
- **Review Trigger:** SMTP 지연 문제가 해소되거나 워커 운영 부담이 더 커질 때, 또는 다른 목적으로 Redis를 운영하게 될 때 다시 봅니다.
- **Implementation:** celery 의존성 추가만 완료로 표시했습니다. 현재 코드는 아직 동기 발송이라, 나머지 작업(Celery 앱과 RabbitMQ 연결 설정, 태스크 전환, 재시도, 테스트, 모니터링)은 체크리스트로 남겼습니다.
- **Reversibility:** Yes / Low. 가입 처리를 직접 호출로 되돌리고 celery를 제거하면 됩니다. 브로커가 기존 RabbitMQ라 따로 정리할 인프라도 없습니다.
- **Evidence** 섹션은 뺐습니다. 측정 수치가 없어서입니다. SMTP 지연 시간이나 가입 API 응답 시간 같은 실측값이 있으면 알려주세요. 추가하겠습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.
