`docs/adr/0002-session-store-redis.md`에 ADR을 작성했습니다(Status: Proposed).

- **번호:** `docs/adr/`에 `0001-record-architecture-decisions.md`가 이미 있어서, 기존 4자리 규칙에 맞춰 ADR-0002로 만들었습니다.
- **Context/Decision:** `app/session.py`가 세션을 모듈 전역 dict(`_sessions`)에 들고 있어서 서버 3대 환경에서는 요청이 다른 서버로 가면 세션을 찾지 못합니다. 이 원인과 `redis==5.0.8` 추가를 근거로 적었습니다. `get`/`put` 인터페이스는 그대로 두고 내부 저장소만 바꾸는 방향으로 기록했습니다.
- **Consequences/Risks:** Redis가 단일 장애점이 되는 점, 전환 배포 때 기존 세션이 사라져 사용자가 한 번 다시 로그인해야 하는 점, 지금 dict에는 만료가 없으니 TTL을 정해야 한다는 점을 넣었습니다.
- **Reversibility:** 코드로는 쉽게 되돌릴 수 있지만(Low), 되돌리면 로그인 풀림 문제가 다시 생긴다고 적었습니다.
- **Evidence 섹션은 뺐습니다.** 로그인 풀림 현상은 들었지만 발생 빈도나 부하 같은 수치가 없어서, 증상은 Context에만 넣었습니다.
- **Alternatives와 Review Trigger 섹션도 뺐습니다.** 검토한 대안이 무엇이고 왜 기각했는지 대화에 없어서, 짐작으로 채우지 않았습니다.

이 결정에서 기각한 대안과 근거를 알려주세요. 예를 들어 로드밸런서 sticky session, DB(SQLAlchemy) 세션 테이블, JWT 같은 무상태 토큰을 검토했는지, 검토했다면 왜 기각했는지 알려주시면 Alternatives와 Review Trigger 섹션을 추가하겠습니다.
