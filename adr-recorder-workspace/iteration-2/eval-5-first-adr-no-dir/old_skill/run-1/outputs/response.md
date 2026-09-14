인증 메일 발송을 Celery 큐로 옮기는 결정을 ADR로 기록했습니다. 저장소의 첫 ADR이라 `docs/adr/` 디렉터리도 새로 만들었어요.

**파일:** `docs/adr/001-signup-verification-email-celery-queue.md`

**어떻게 채웠나**
- **Status:** 새로 내리는 결정이라 Proposed로 뒀습니다.
- **Decision Source:** Human입니다. 말씀하신 결정을 그대로 옮긴 거라 Confidence는 넣지 않았습니다.
- **Context / Decision:**
  - 문제는 SMTP가 느릴 때 가입 API도 같이 느려진다는 점입니다.
  - 제약은 이미 운영 중인 RabbitMQ를 브로커로 재사용한다는 점입니다.
  - 선택안은 Celery(`celery>=5.4`, `pyproject.toml` 변경분 반영)입니다.
- **Alternatives:** RQ를 넣었습니다. Redis를 새로 운영해야 해서 뺐다고 적었고, Redis를 다른 용도로 도입하게 되면 다시 검토하도록 Review Trigger에 걸어뒀습니다.
- **Implementation:** 체크리스트에서 celery 의존성 추가는 완료로, task 분리·브로커 설정·테스트·모니터링은 남은 작업으로 표시했습니다.
- **Reversibility:** Yes / Low입니다. enqueue를 동기 호출로 되돌리면 원복됩니다.
- **References:** 기존 동기 발송을 넣은 커밋 `9ef6bd8`을 적었습니다.
- **Evidence:** 실측 수치가 없어서 섹션을 만들지 않았습니다. RQ의 장점(Pros)도 말씀하신 적이 없어 비워두는 대신 줄을 뺐습니다.

이 결정에서 기각한 대안과 수치적 근거를 알려주세요. 예를 들면 이런 것들입니다.
- SMTP가 느릴 때 가입 API 응답 시간(p95 등)이 얼마나 늘었는지
- Redis를 새로 운영하는 데 드는 비용·공수
- RQ 말고 검토했던 다른 방식이 있는지 (예: FastAPI BackgroundTasks, 동기 발송 유지)

알려주시면 Evidence와 Alternatives에 반영하겠습니다.
