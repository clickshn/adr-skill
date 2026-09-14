ADR을 작성했습니다: `docs/adr/0002-redis-session-store.md`

기존 `docs/adr/`에 `0001-record-architecture-decisions.md`가 있어 번호는 0002로 이어 붙였습니다.

정리한 내용

- **Status:** 새로 내리는 결정이라 `Proposed`로 시작했습니다. `requirements.txt`에 `redis==5.0.8`이 이미 들어가 있지만 `app/session.py`는 아직 인메모리 dict라 구현은 남아 있습니다.
- **Context:** 세션이 `app/session.py`의 모듈 전역 `_sessions` dict에 있어 인스턴스에 묶이고, 3대로 늘리면서 요청이 다른 인스턴스로 가면 로그인이 풀리는 상황으로 적었습니다.
- **Decision:** `get`/`put` 시그니처는 유지하고 내부 구현만 Redis로 교체하는 방향으로 잡았습니다. 세션 접근이 이 두 함수로만 이루어져 있어 호출부는 건드리지 않아도 됩니다.
- **Alternatives:** 대화에 나온 "현행 유지(프로세스 메모리)" 하나만 기각 사유(3대 구성에서 로그인 풀림)와 함께 적었습니다.
- **Consequences/Risks:** Redis가 단일 장애점이 되는 점, 세션 직렬화 형식·TTL 정책을 새로 정해야 하는 점, 전환 시점에 기존 세션이 무효화되어 재로그인이 발생하는 점을 적어 두었습니다.
- **Reversibility:** `app/session.py`를 되돌리고 `requirements.txt`에서 redis를 빼면 되는 수준이라 Yes / Migration Cost Low로 봤습니다.

비워 둔 것

- **Evidence 섹션은 만들지 않았습니다.** 벤치마크나 프로덕션 측정치가 없어서, "로그인이 풀린다"는 관찰은 Context에 두었습니다. 세션 조회 지연이나 Redis 용량 같은 수치가 있으면 알려주시면 채워 넣겠습니다.
- **Review Trigger도 만들지 않았습니다.** 재검토 조건이 대화에 없었는데, 기각 사유를 뒤집은 조건("단일 서버로 돌아가면")은 지어낸 것이라 쓰지 않았습니다.
- 스티키 세션이나 DB 세션 테이블처럼 같이 검토했다가 접은 대안이 있었다면 그 근거를 알려주세요. Alternatives에 추가하겠습니다. 없었다면 지금 상태로 두면 됩니다.

`docs/adr/` 밖의 파일(`app/session.py`, `requirements.txt` 등)은 건드리지 않았습니다.
