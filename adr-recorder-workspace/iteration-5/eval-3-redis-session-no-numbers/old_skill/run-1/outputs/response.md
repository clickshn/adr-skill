ADR을 작성했습니다: `docs/adr/0002-store-sessions-in-redis.md`

**번호:** `docs/adr/`에 이미 `0001-record-architecture-decisions.md`가 있어서 그 네 자리 형식을 따라 다음 번호인 **0002**로 만들었습니다.

**담긴 내용**
- **Status:** Proposed. `app/session.py`가 아직 프로세스 메모리 딕셔너리(`_sessions`)를 쓰고 있어서 구현 전 상태로 뒀습니다. 적용이 끝나면 Accepted로 바꾸시면 됩니다.
- **Decision Source:** Human. 사용자가 직접 내린 결정이라 Confidence 필드는 뺐습니다.
- **Context:** 인메모리 세션 때문에 서버를 3대로 늘리자 로그인이 풀리는 문제, 기존 `get`/`put` 인터페이스, `redis==5.0.8` 추가.
- **Consequences / Implementation:** 코드를 확인하다 발견한 점도 넣었습니다. 지금의 `put`에는 만료 처리가 없어서 Redis로 옮길 때 TTL을 정하지 않으면 세션 키가 계속 쌓입니다. 이 밖에 Redis 단일 장애점, 전환할 때 로그인 중인 사용자는 다시 로그인해야 한다는 점도 적었습니다.
- **Reversibility:** 되돌릴 수 있고(Yes) 비용은 Low입니다. 세션 모듈만 원래대로 돌리면 되지만, 그러면 다중 서버에서 로그인이 풀리는 문제가 다시 생깁니다.
- **빠진 섹션:** 측정 수치가 없어서 Evidence는 넣지 않았습니다. 기각한 대안도 대화에 없어서 Alternatives와 Review Trigger는 추측으로 채우지 않고 뺐습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.

이 결정에서 기각한 대안과 근거를 알려주세요. 예를 들어 로드밸런서 스티키 세션, JWT 같은 무상태 토큰, DB 세션 테이블을 검토했다면 각각 왜 제외했는지 알려주시면 Alternatives와 Review Trigger 섹션을 추가하겠습니다.
