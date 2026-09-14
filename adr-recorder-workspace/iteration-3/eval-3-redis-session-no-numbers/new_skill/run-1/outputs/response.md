ADR 작성했습니다: `docs/adr/0002-move-session-store-to-redis.md`

- **번호:** 기존 `0001-record-architecture-decisions.md`가 4자리 번호를 쓰고 있어서 이번 ADR은 `ADR-0002`로 맞췄습니다.
- **Status: Proposed:** `requirements.txt`에 `redis==5.0.8`만 추가됐고 `app/session.py`는 아직 dict 기반이라, 결정은 내렸지만 시행 전 상태로 기록했습니다.
- **Decision Source: Human:** 직접 내리신 결정이라 Confidence 필드는 뺐습니다. Evidence에는 "서버 3대 증설 후 로그인 풀림 관측"만 적었습니다. 발생 빈도 같은 수치는 알려주신 게 없어서 수치 없음으로 표기했고 추정값은 넣지 않았습니다.
- **저장소에서 확인한 내용:**
  - 세션 접근이 `get`/`put` 두 함수로 묶여 있어서 이 모듈만 바꾸면 됩니다.
  - 지금 구현에는 **세션 만료가 없어서** 그대로 옮기면 Redis에 세션이 계속 쌓입니다. 그래서 Risks와 Implementation에 TTL 설정을 넣었습니다.
  - Redis가 단일 장애점이 된다는 점도 Risks에 적었습니다.
- **Reversibility:** 코드를 되돌리고 의존성을 빼면 롤백되므로 Migration Cost는 Low로 적었습니다. 다만 롤백하면 3대 구성에서 로그인 풀림 문제가 다시 생긴다고 함께 적어 두었습니다.

Alternatives와 Review Trigger 섹션은 비워 두지 않고 아예 뺐습니다. 기각한 대안에 대한 내용이 대화에 없었고, 추측으로 채우지 않기 위해서입니다.

이 결정에서 기각한 대안과 근거를 알려주세요. 예를 들어 로드밸런서 sticky session, 기존 DB(SQLAlchemy)에 세션 테이블 두기, JWT 같은 무상태 토큰 등을 검토하셨다면, 각각 왜 기각했고 어떤 조건이면 다시 볼지 알려주세요. 받은 내용으로 Alternatives와 Review Trigger를 추가하겠습니다.
