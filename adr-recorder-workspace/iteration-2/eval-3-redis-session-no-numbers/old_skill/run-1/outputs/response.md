ADR을 작성했어요: `docs/adr/0002-move-session-store-to-redis.md` (Status: Proposed)

**기록한 내용**
- **Problem:** 세션이 `app/session.py`의 프로세스 메모리 dict(`_sessions`)에 저장돼 있어요. 서버를 3대로 늘리자 요청이 로그인한 서버가 아닌 다른 서버로 가면 세션을 못 찾아 로그인이 풀려요.
- **Decision:** 세션 저장소를 Redis로 옮겨 3대가 함께 쓰도록 해요. `requirements.txt`에 들어간 `redis==5.0.8`을 그대로 반영했어요.
- **Consequences:** 좋아지는 점은 멀티 인스턴스에서 로그인 유지, 재시작·배포 후에도 세션 유지예요. 부담은 Redis 운영이 늘고, 세션마다 네트워크 왕복과 직렬화가 생기는 거예요.
- **Risks:** Redis가 단일 장애점이 돼요. 또 지금 코드에는 세션 만료·삭제 로직이 없어서, TTL을 정하지 않고 옮기면 세션 키가 계속 쌓여요.
- **Implementation / Reversibility:** 구현 체크리스트를 넣었어요. 롤백 비용은 Low로 적었어요.

**비워 둔 섹션**
- Evidence, Alternatives, Review Trigger는 넣지 않았어요. 대화에 수치나 비교한 대안이 없어서 추측으로 채우지 않았어요.
- Decision Source는 Human이라 Confidence 필드는 생략했어요.

이 결정에서 기각한 대안과 수치적 근거를 알려주세요. 예를 들면 sticky session, DB 기반 세션, JWT 같은 대안을 검토했는지, 그리고 그때 본 지연·비용·장애율 수치가 있는지요. 알려주시면 Alternatives와 Review Trigger 섹션을 채울게요.
