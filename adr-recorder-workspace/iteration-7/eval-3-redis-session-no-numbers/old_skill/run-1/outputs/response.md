ADR을 작성했습니다: `docs/adr/0002-store-sessions-in-redis.md`

- **번호:** `docs/adr/`에 이미 `0001-record-architecture-decisions.md`(ADR-0001)가 있어서, 기존 4자리 번호 규칙에 맞춰 **ADR-0002**로 만들었습니다.
- **Status:** Proposed. 새로 내린 결정이라서 `requirements.txt`에 `redis==5.0.8`이 이미 들어가 있어도 Proposed로 시작합니다.
- **Decision Source:** Human. 직접 내리신 결정이라 Confidence 필드는 뺐습니다.
- **Context:** 지금 `app/session.py`는 모듈 전역 dict(`_sessions`)에 세션을 저장합니다. 그래서 서버를 3대로 늘리면 요청이 다른 서버로 갔을 때 세션을 찾지 못해 로그인이 풀립니다. 이 문제를 배경으로 적었습니다.
- **Implementation:** 의존성 추가만 완료로 표시했습니다. `app/session.py`는 아직 dict 기반 그대로라서 Redis로 교체하는 작업은 미완료 항목으로 남겼습니다.
- **Risks에 추가한 발견:** 지금 구현에는 세션 만료(TTL)가 없습니다. 그대로 옮기면 Redis에 세션이 계속 쌓이므로 만료 정책을 함께 정해야 한다고 적었습니다. Redis 장애 시 로그인 전체가 불가능해지는 점(단일 장애점)과, 전환 시점에 기존 세션이 사라져 한 번 재로그인해야 하는 점도 적었습니다.
- **Reversibility:** Yes / Low. 세션 모듈이 `get`/`put` 두 함수뿐이라 되돌리기 쉽습니다. 다만 여러 서버에서 되돌리면 원래 문제가 다시 생긴다고 명시했습니다.
- **생략한 섹션:** 대화에 측정 수치가 없어서 Evidence는 만들지 않았습니다. 대화에 나온 대안이 없어서 Alternatives와 Review Trigger도 만들지 않았습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.

**이 결정에서 기각한 대안과 근거를 알려주세요.** 예를 들어 Redis 대신 검토했지만 선택하지 않은 방식이 있다면 알려주세요. 알려주시면 Alternatives와 Review Trigger 섹션을 추가하겠습니다.
