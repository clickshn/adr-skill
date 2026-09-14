ADR을 작성했습니다: `docs/adr/0002-session-store-redis.md`

기존 `docs/adr/0001-record-architecture-decisions.md`가 있어서 다음 번호인 0002로 매겼습니다.

**ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전**

- **Status:** Proposed — 새로 내리는 결정이라 `requirements.txt`가 이미 바뀌어 있어도 Proposed로 시작했습니다.
- **Context:** `app/session.py`의 `_sessions` dict에 세션이 프로세스별로 갇혀 있고, 서버 3대 확장 후 다른 인스턴스로 라우팅된 요청에서 로그인이 풀리는 문제.
- **Decision:** Redis(redis-py 5.0.8)를 공유 세션 스토어로 두고, `get`/`put`을 Redis 호출로 교체 + TTL 부여.
- **Alternatives:** 말씀하신 현행(프로세스 메모리 유지)을 기각 대안으로 정리했고, 기각 사유는 3대 확장 시 로그인 풀림입니다.
- **Consequences:** Redis가 단일 장애점이 되는 점, 조회마다 네트워크 왕복이 느는 점, 세션 TTL 누락 시 키가 쌓이는 점을 리스크로 적었습니다.
- **Reversibility:** Yes — `app/session.py`를 `ba84cb2` 시점 구현으로 되돌리고 `requirements.txt`에서 redis 제거. 단 롤백하면 3대 구성에서 문제가 재발하므로 인스턴스 축소가 동반돼야 한다고 명시했습니다.

재검토 조건(Recheck if)은 대화에 명시된 게 없어서 비워뒀고, 그래서 Review Trigger 섹션도 만들지 않았습니다. 측정 수치가 없어 Evidence 섹션도 생략했습니다. 나중에 "지연 시간이 N ms를 넘으면 재검토" 같은 조건이 정해지면 알려주시면 채워 넣겠습니다.
