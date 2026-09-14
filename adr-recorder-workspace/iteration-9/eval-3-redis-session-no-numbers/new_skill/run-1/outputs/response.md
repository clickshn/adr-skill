세션 저장소를 Redis로 옮기는 결정을 ADR로 작성했습니다.

**생성 파일:** `docs/adr/0002-move-session-store-to-redis.md`

- **번호:** `docs/adr/`에 이미 `0001-record-architecture-decisions.md`가 있습니다. 그래서 기존 네 자리 형식을 따라 ADR-0002로 만들었습니다.
- **Status:** Proposed입니다. 새로 내리는 결정이라, requirements.txt가 이미 바뀌었어도 Proposed로 시작합니다.
- **Decision Source:** Human입니다. 직접 내리신 결정이라 Confidence 필드는 넣지 않았습니다.
- **Context / Rationale:** 세션이 프로세스 메모리에 있으면 서버 3대로 늘렸을 때 로그인이 풀린다는 점을 적었습니다. Redis로 옮기면 세션을 여러 서버가 공유하고, `get`/`put` 인터페이스를 유지해 변경 범위가 작다는 점도 적었습니다.
- **Evidence:** 실측 수치가 없어 이 섹션은 만들지 않았습니다.
- **Alternatives:** 대화에 나온 대안은 "현행 유지(프로세스 메모리)"뿐이라 이것만 적었습니다. 기각 사유는 "서버 3대에서 로그인이 풀림"입니다. 대화에 재검토 조건이 없어 Recheck if 줄과 Review Trigger 섹션은 생략했습니다.
- **Implementation:** requirements.txt에 `redis==5.0.8`을 추가한 항목은 완료로 표시했습니다. `app/session.py`는 아직 `_sessions` dict 기반이라 Redis로 교체하는 작업(세션 dict 직렬화 포함)을 미완료 항목으로 남겼습니다.
- **Reversibility:** Yes / Migration Cost Low입니다. 되돌리면 Redis에 있던 세션이 사라지고, 서버 3대 구성에서는 로그인이 풀리는 문제가 다시 생긴다고 롤백 항목에 적었습니다.
- **Risks:** Redis가 장애 나면 전체 서버의 로그인에 영향을 준다는 점을 적었습니다. 지금 코드에도 세션 만료(TTL) 로직이 없어, 설정하지 않으면 Redis에 세션이 계속 쌓일 수 있다는 점도 적었습니다.

`docs/adr/` 밖의 파일(`app/session.py`, requirements.txt 등)은 수정하지 않았습니다.
