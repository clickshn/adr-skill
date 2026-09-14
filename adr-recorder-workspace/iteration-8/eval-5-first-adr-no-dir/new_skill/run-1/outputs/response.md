ADR을 작성했습니다: `docs/adr/001-celery-verification-email-queue.md`

- 저장소에 `docs/adr/` 디렉터리가 없었습니다. 그래서 디렉터리를 새로 만들고 첫 ADR 번호를 **001**로 시작했습니다.
- **Status: Proposed**로 두었습니다. 새로 내린 결정이라 코드 변경 여부와 상관없이 Proposed에서 시작합니다.
- **Decision Source: Human**이라 Confidence는 넣지 않았습니다.
- 담은 내용:
  - Context: `app/mail.py`의 `send_verification()`이 요청 처리 중 `smtp.internal:25`로 동기 발송하고 있어서, SMTP가 느리면 가입 API도 같이 느려집니다.
  - Decision: Celery(`celery>=5.4`)를 쓰고, 브로커는 운영 중인 RabbitMQ를 씁니다.
  - Alternatives: RQ(Redis를 새로 운영해야 해서 제외)와 현행 동기 발송 유지를 적었습니다.
  - Reversibility: 동기 호출로 되돌리고 celery를 빼면 되므로 Yes / Low입니다.
- 넣지 않은 섹션:
  - Evidence: 측정 수치가 없습니다. SMTP 지연은 정성적 관찰로 보고 Context에 적었습니다.
  - Review Trigger: 대화에 재검토 조건(Recheck if)이 없었습니다.
- 참고: 지금 `app/mail.py`는 아직 동기 발송 그대로이고, `pyproject.toml`의 celery 추가도 아직 커밋되지 않았습니다. 두 가지 모두 Implementation 체크리스트에 넣었습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.
