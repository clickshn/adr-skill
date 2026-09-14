ADR을 새로 작성했습니다: `docs/adr/0002-session-store-redis.md`

기존 ADR이 `0001-record-architecture-decisions.md` 하나 있어서 그 번호 체계를 이어 **0002**로 붙였습니다.

작성 내용 요약:

- **Status: Proposed** — requirements.txt에 `redis==5.0.8`이 이미 추가되어 있지만, 기존 결정 로그를 옮겨 적은 게 아니라 이번에 새로 내린 결정이라 Proposed로 시작했습니다.
- **Context** — `app/session.py`의 `_sessions` 딕셔너리가 프로세스 로컬이라 3대 분산 시 로그인이 풀리는 문제를 문제/제약으로 정리했습니다.
- **Decision / Rationale** — 세션 접근이 `get`/`put` 두 함수로 격리되어 있어 교체 범위가 좁다는 점을 근거에 포함했습니다.
- **Reversibility** — 롤백은 `app/session.py`를 커밋 `bd074f7` 시점 구현으로 되돌리고 requirements.txt에서 redis 줄을 제거하는 방식, 활성 세션은 유지되지 않는다는 점을 적었습니다.
- 측정 수치(지연, 에러율 등)로 받은 게 없어 **Evidence 섹션은 만들지 않았고**, 재검토 조건이 언급되지 않아 Recheck if / Review Trigger도 넣지 않았습니다.

한 가지 확인 부탁드립니다. Alternatives에는 대화에서 확인된 "현행 유지(프로세스 메모리)" 하나만 적었습니다. 이 결정에서 기각한 다른 대안과 그 근거를 알려주세요 (예: 어떤 후보를 왜 제외했는지). 알려주시면 Alternatives 섹션에 추가하겠습니다. 추측으로 채워 넣지는 않았습니다.
