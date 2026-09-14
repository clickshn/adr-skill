ADR을 작성했습니다: `docs/adr/0002-move-session-store-to-redis.md`

- **번호:** `docs/adr/`에 이미 `0001-record-architecture-decisions.md`가 있어서, 그 4자리 형식에 맞춰 ADR-0002로 만들었습니다.
- **Status:** Proposed. `requirements.txt`에 `redis==5.0.8`가 이미 추가되어 있지만, 새로 내린 결정이라 Proposed로 시작합니다.
- **Context:** 지금 세션은 `app/session.py`의 모듈 전역 dict `_sessions`에 들어 있습니다. 그래서 서버를 3대로 늘리면 로그인한 서버와 다른 서버로 요청이 갈 때 로그인이 풀립니다.
- **Decision:** `get`/`put` 시그니처는 그대로 두고 내부 저장소만 Redis로 바꿉니다. 교체 범위는 `app/session.py` 하나입니다. 지금은 의존성만 추가됐고 코드는 아직 안 바뀌었다고 적었습니다.
- **Consequences / Implementation:** 다음 내용을 정리했습니다.
  - Redis 장애가 SPOF가 될 수 있다는 점
  - 세션 TTL과 직렬화가 필요하다는 점
  - 전환할 때 기존 세션이 사라져 한 번 재로그인해야 한다는 점
  - 여러 인스턴스에서 세션이 유지되는지 확인하는 테스트
  - Redis 접속 정보를 환경 변수로 빼는 작업
- **Reversibility:** Yes / Low. `session.py`와 `requirements.txt`만 되돌리면 되지만, 그러면 3대 구성에서 로그인 풀림 문제가 다시 생긴다고 적었습니다.
- **작성하지 않은 섹션:**
  - **Evidence:** 측정 수치가 없어서 뺐습니다.
  - **Alternatives, Review Trigger:** 대화에 나온 대안이 없어서 둘 다 뺐습니다.
  - **Confidence:** 사람이 내린 결정이라 생략했습니다.

`docs/adr/` 밖의 파일(`app/session.py` 등)은 수정하지 않았습니다.

이 결정에서 기각한 대안과 근거를 알려주세요.
