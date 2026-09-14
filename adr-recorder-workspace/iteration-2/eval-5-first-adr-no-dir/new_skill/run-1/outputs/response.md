ADR을 남겼습니다: `docs/adr/001-signup-email-celery-queue.md`

- 저장소에 기존 ADR이 없고 `docs/adr/` 디렉터리도 없어서, 이번에 새로 만들고 첫 번호인 **ADR-001**로 작성했습니다.
- **Status:** Proposed (새로 내린 결정이므로), **Decision Source:** Human (그래서 Confidence 필드는 뺐습니다)
- **Context / Decision:** SMTP가 느리면 가입 API도 같이 느려지는 문제 → 인증 메일 발송을 Celery task로 옮기고, 브로커는 이미 운영 중인 RabbitMQ 사용 (`pyproject.toml`의 `celery>=5.4` 반영)
- **Alternatives:** RQ — Redis를 새로 운영해야 해서 기각. Recheck if: Redis를 다른 용도로 운영하게 되거나 RabbitMQ를 교체하는 경우 (이 내용을 Review Trigger에도 넣었습니다)
- **Consequences / Risks:** 워커 운영 부담, 가입 응답 시점에 발송 성공 여부를 알 수 없음, 워커 중단·큐 적체 시 메일 지연·누락, 재시도 시 중복 발송, RabbitMQ 장애 시 작업 등록 실패 처리 필요
- **Implementation:** task 전환·워커 구성·재시도 정책, 테스트, 큐 길이/실패율 모니터링, 워커 배포 문서화 체크리스트
- **Reversibility:** Yes / Low — 동기 호출로 되돌리고 celery를 빼면 원복됩니다.
- **References:** 기존 동기 발송 구현 커밋 `9ef6bd8`와 `pyproject.toml` 변경을 적었습니다.

SMTP 지연이나 가입 API 응답 시간 실측치가 없어서 Evidence 섹션은 만들지 않았습니다. 수치가 있으면 알려주세요. Evidence로 추가하겠습니다.
