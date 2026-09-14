ADR 남겼어요. 저장소에 ADR이 하나도 없어서 `docs/adr/` 디렉터리를 새로 만들고 첫 번호로 생성했습니다.

**`docs/adr/ADR-001-signup-email-celery-queue.md`**

- **Status:** Proposed. 새로 내린 결정이라 Proposed로 뒀어요. 구현이 끝나면 Accepted로 바꾸면 됩니다.
- **Decision Source:** Human. 직접 내린 결정이라 Confidence 필드는 뺐습니다.
- **Context:** SMTP가 느리면 가입 API가 같이 느려지는 문제. 새 인프라 없이 기존 RabbitMQ를 쓴다는 제약.
- **Decision:** 가입 API는 메일 작업을 큐에 넣기만 하고, 실제 발송은 Celery 워커가 합니다(`celery>=5.4`, 브로커 RabbitMQ).
- **Alternatives:** RQ는 Redis를 새로 운영해야 해서 기각했어요. 재검토 조건은 "Redis를 다른 용도로 도입하게 될 때"로 적었고, Review Trigger에도 같이 넣었습니다.
- **Consequences:** 워커를 따로 운영해야 하고, 가입 응답 시점에는 발송 성공 여부를 알 수 없어요. 워커나 브로커 장애 때 메일이 지연되거나 누락될 수 있고, 재시도 설정에 따라 중복 발송될 수도 있어서 리스크로 적었습니다.
- **Implementation:** 체크리스트로 적었고, celery 의존성 추가만 완료로 표시했어요.
- **Reversibility:** 동기 호출로 되돌리고 워커를 내리면 돼서 Yes / Low.
- **References:** 기존 동기 발송 커밋 `1c47568`과, `pyproject.toml` 변경이 아직 커밋 전이라는 점만 적었습니다.

실측 수치(SMTP 지연 시간, 가입 API p95 등)가 없어서 Evidence 섹션은 만들지 않았어요. 수치가 있으면 알려주세요. 추가할게요.
