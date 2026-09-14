인증 메일 Celery 전환 결정을 ADR로 남겼습니다.

**생성 파일:** `docs/adr/001-async-verification-email-with-celery.md`

저장소에 `docs/adr/` 디렉터리가 없어서 새로 만들었고, 기존 ADR이 없으므로 번호는 **001**부터 시작했습니다.

**담은 내용**
- **Context:** 지금 `app/mail.py`의 `send_verification`은 가입 요청을 처리하면서 `smtp.internal:25`로 메일을 동기 발송합니다. 그래서 SMTP가 느려지면 가입 API도 같이 느려집니다. 제약은 기존 RabbitMQ를 재사용하고 새 인프라를 늘리지 않는 것입니다.
- **Decision:** Celery(`celery>=5.4`, `pyproject.toml` diff로 확인)로 메일 발송을 워커에서 비동기 처리하고, 브로커는 기존 RabbitMQ를 씁니다.
- **Alternatives:** RQ는 Redis를 새로 운영해야 해서 기각했습니다. Recheck 조건은 "Redis를 이미 운영하게 되거나 RabbitMQ 운영을 중단할 경우"이고, 이 조건을 Review Trigger에도 넣었습니다.
- **Consequences:** 워커 운영 부담이 생기고, API가 성공한 뒤에 메일 발송이 실패할 수 있습니다. 재시도 설정에 따라 중복 발송이 생길 수 있고, 인증 토큰이 브로커 메시지에 남는 점도 리스크로 적었습니다.
- **Reversibility:** 발송 함수 호출 지점이 하나라서 동기 호출로 되돌리기 쉽습니다(Low).
- **References:** 동기 발송 도입 커밋 `558ed63`, `app/mail.py`, `pyproject.toml`

**참고**
- Status는 템플릿 기본값인 **Proposed**로 두었습니다. 아직 `mail.py`가 동기 발송 상태라서, 전환이 끝나면 Accepted로 바꾸면 됩니다.
- 대화에 SMTP 지연 시간 같은 실측 수치가 없어서 Evidence 섹션은 만들지 않았습니다. 수치가 있으면 알려주세요. Evidence에 추가하겠습니다.
- `docs/adr/` 밖의 파일은 수정하지 않았습니다.
