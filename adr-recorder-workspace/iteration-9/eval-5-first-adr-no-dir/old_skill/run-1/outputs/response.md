`docs/adr/` 디렉터리가 없어 기존 ADR이 없는 상태라 **ADR-001**부터 시작했습니다.

**생성한 파일:** `docs/adr/001-async-verification-mail-celery.md`

**ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화**

- **Status: Proposed.** 새로 내린 결정이라 Proposed로 시작합니다. `pyproject.toml`에 이미 celery가 추가된 것과는 상관없습니다. 팀에서 확정되면 Accepted로 바꿔 주세요.
- **Decision Source: Human.** 규칙에 따라 Confidence 필드는 뺐습니다.
- **Context:** `app/mail.py`의 `send_verification()`이 가입 요청 처리 중에 `smtp.internal:25`로 동기 발송합니다. `smtplib.SMTP(...)`에 timeout 인자가 없어서 SMTP 지연이 가입 API 응답에 그대로 전파됩니다. 이 내용을 Problem에 한 줄로 넣었습니다.
- **Decision:** Celery(`celery>=5.4`)를 쓰고 브로커는 이미 운영 중인 RabbitMQ로 합니다. 가입 API는 발송 작업을 enqueue만 하고 워커가 SMTP로 발송합니다.
- **Alternatives:** RQ는 Redis를 새로 운영해야 해서 기각했습니다. 말씀하신 근거를 그대로 적었고, Recheck if(다른 목적으로 Redis를 운영하게 될 때)는 Review Trigger에도 모아 두었습니다.
- **Evidence:** SMTP 지연 시간이나 가입 API 응답 시간 같은 실측 수치가 대화와 저장소에 없어서 이 섹션은 만들지 않았습니다.
- **Implementation:** celery 의존성 추가만 완료로 체크했습니다. 나머지 항목(Celery 앱과 RabbitMQ 설정, task 전환과 enqueue, timeout과 재시도, 워커 배포, 테스트, 모니터링)은 미완료로 남겼습니다.
- **Reversibility:** Yes / Low입니다. 직접 호출로 되돌리고 워커를 내린 뒤 celery를 제거하면 됩니다. 브로커가 기존 RabbitMQ라 따로 철거할 인프라가 없습니다.
- **References:** Documentation에 동기 발송 구현 커밋 `c44bbf9`와 미커밋 `pyproject.toml` 변경을 적었습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.
