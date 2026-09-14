ADR을 `docs/adr/001-celery-async-verification-email.md`에 작성했습니다.

저장소에 `docs/adr/` 디렉터리가 없어서 새로 만들었고, 이번이 첫 ADR이라 **ADR-001**로 시작했습니다.

**ADR-001: 회원가입 인증 메일 발송을 Celery 작업 큐로 비동기화**
- **Status:** Proposed. 새로 내린 결정이고 코드 전환은 아직 안 됐습니다(`app/mail.py`는 여전히 동기 발송).
- **Decision Source:** Human. 직접 내리신 결정이라 Confidence 필드는 뺐습니다.
- **Context:** `send_verification()`이 요청 처리 중에 `smtp.internal:25`로 동기 발송해서, SMTP가 느리면 가입 API도 느려집니다.
- **Decision:** Celery(`celery>=5.4`, pyproject.toml 변경분 확인) + 기존 운영 중인 RabbitMQ 브로커. API는 작업을 큐에 넣고 바로 응답하고, 발송은 워커가 합니다.
- **Alternatives:** RQ. Redis를 새로 운영해야 해서 기각했습니다. 다시 볼 조건(Recheck if)은 "Redis를 다른 목적으로 운영하게 될 때"이고, Review Trigger에도 넣었습니다.
- **Consequences / Risks:** 워커 운영 부담이 생기고, API 응답 시점에는 메일이 실제로 나갔는지 알 수 없습니다. 재시도 정책이 없으면 메일이 유실될 수 있고, 설정에 따라서는 중복 발송될 수 있습니다. 인증 토큰이 브로커에 저장되고, RabbitMQ를 다른 워크로드와 공유하게 됩니다.
- **Implementation:** Celery 앱과 브로커 설정, task 전환과 재시도, `.delay()` 호출로 교체, 워커 배포, 테스트, 큐 모니터링을 체크리스트로 넣었습니다.
- **Reversibility:** Yes / Low. 동기 호출로 되돌리고 celery와 워커를 걷어내면 됩니다. 되돌리기 전에 큐에 남은 작업은 먼저 처리해야 합니다.

실측 수치(SMTP 지연 시간, 가입 API 응답 시간 등)가 대화에 없어서 Evidence 섹션은 만들지 않았습니다. 수치가 있으면 알려주세요. Evidence에 추가하겠습니다.
