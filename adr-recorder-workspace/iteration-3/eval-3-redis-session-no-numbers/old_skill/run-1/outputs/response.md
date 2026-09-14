`docs/adr/0002-store-sessions-in-redis.md`에 ADR-0002를 작성했어요.

- **Status:** Proposed / **Decision Source:** Human (그래서 Confidence는 넣지 않았어요)
- **Context:** `app/session.py`가 세션을 프로세스 전역 dict에 저장하고 있어서, 서버를 3대로 늘리자 다른 서버로 요청이 가면 로그인이 풀리는 문제
- **Decision:** `get`/`put` 인터페이스는 그대로 두고 내부 저장소만 Redis(`redis==5.0.8`)로 교체
- **Consequences / Implementation / Reversibility:** Redis 장애 시 단일 장애점이 되는 위험, 세션 TTL, 직렬화, 접근 제어를 적고 구현 체크리스트를 넣었어요. 롤백은 가능하지만 되돌리면 원래 문제가 다시 생기므로 Partial로 적었어요.
- **References:** `requirements.txt` 변경(아직 커밋 전), `app/session.py`, 로그인 API 커밋 e776c53

측정 수치가 없어서 Evidence 섹션은 만들지 않았어요. 검토한 대안에 대한 이야기도 없어서 Alternatives와 Review Trigger 섹션도 비워 두지 않고 아예 만들지 않았어요.

이 결정에서 기각한 대안과 근거를 알려주세요. 예를 들어 로드밸런서 sticky session, DB(SQLAlchemy) 세션 테이블, 서명 쿠키/JWT 같은 무상태 토큰이나 Memcached를 검토했다면, 어떤 이유로 제외했는지와 어떤 상황이 되면 다시 볼지 알려주세요. 그러면 Alternatives와 Review Trigger 섹션을 채워 넣을게요.
