ADR을 작성했습니다: `docs/adr/0002-redis-session-store.md`

- **번호:** docs/adr/에 이미 `0001-record-architecture-decisions.md`가 있어서, 그 4자리 번호 규칙을 따라 0002로 만들었습니다.
- **Status:** 아직 구현 전이라 Proposed로 두었습니다. Redis 전환이 배포되면 Accepted로 바꾸면 됩니다.
- **내용:** 서버 3대 증설 시 로그인이 풀리는 문제(Context), Redis 공유 세션 저장소와 `redis==5.0.8`(Decision), 구현 체크리스트, 롤백 방법을 적었습니다. `app/session.py`가 `get`/`put` 두 함수만 노출하고 있어서, 호출부는 그대로 두고 저장소만 교체하는 방식으로 기록했습니다.
- **코드에서 확인한 주의점(Risks에 기록):**
  - Redis가 단일 장애 지점이 됩니다.
  - 지금 세션 코드에는 만료(TTL) 로직이 없어서, 그대로 옮기면 Redis에 세션 키가 계속 쌓입니다.
  - FastAPI 비동기 핸들러에서 동기 redis 클라이언트를 쓰면 이벤트 루프가 막힐 수 있습니다.
- **비워 둔 섹션:** 측정 수치가 없어서 Evidence는 넣지 않았습니다. 기각한 대안도 대화에 나오지 않아 Alternatives와 Review Trigger는 만들지 않았습니다.

이 결정에서 기각한 대안과 근거를 알려주세요. 예를 들어 로드밸런서 sticky session, DB(SQLAlchemy) 기반 세션 저장, 서명 쿠키/JWT 같은 무상태 토큰을 검토했는지, 검토했다면 왜 뺐는지 알려주시면 Alternatives와 Review Trigger 섹션을 추가하겠습니다.
