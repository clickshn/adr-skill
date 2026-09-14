ADR을 작성했습니다: `docs/adr/0002-move-session-store-to-redis.md`

**작성 내용**
- **번호:** 기존 `0001-record-architecture-decisions.md`의 4자리 형식을 따라 ADR-0002로 만들었습니다.
- **Context:** `app/session.py`는 모듈 전역 dict(`_sessions`)에 세션을 저장해서 프로세스마다 세션이 따로 있습니다. 서버를 3대로 늘리면 다른 서버로 간 요청이 세션을 찾지 못해 로그인이 풀립니다. 코드를 보니 세션 만료(TTL) 처리도 없어서 이것도 함께 적었습니다.
- **Decision:** Redis(`redis==5.0.8`)를 공유 세션 저장소로 쓰고, `get`/`put` 인터페이스는 그대로 두고 내부 구현만 바꾸는 방식으로 적었습니다.
- **Consequences:** Redis가 단일 장애점이 되는 것, 전환 시점에 기존 사용자가 다시 로그인해야 하는 것, 세션을 직렬화해야 하는 것, Redis 접근 제어가 필요한 것을 적었습니다.
- **Reversibility:** 코드는 되돌리기 쉽습니다(Migration Cost: Low). 다만 서버 3대 구성 그대로 되돌리면 로그인이 다시 풀리니 sticky session을 쓰거나 서버를 1대로 줄여야 한다고 적었습니다.
- **Status:** 아직 `session.py`가 dict로 되어 있어 **Proposed**로 두었습니다. 구현이 끝나면 Accepted로 바꾸세요.

**비워둔 부분**
- **Evidence / Confidence:** 측정 수치가 없어서 Evidence는 만들지 않았습니다. 직접 내린 결정(Decision Source: Human)이라 Confidence도 뺐습니다.
- **Alternatives / Review Trigger:** 대화에 대안을 기각한 이유가 없어서 추측으로 채우지 않고 두 섹션 모두 만들지 않았습니다.

`docs/adr/` 밖의 파일(requirements.txt, app/session.py 포함)은 수정하지 않았습니다.

이 결정에서 기각한 대안과 근거를 알려주세요. 예를 들어 로드밸런서 sticky session, DB 세션 테이블, JWT 같은 토큰 방식을 검토하셨다면 각각 왜 기각했는지, 어떤 조건이면 다시 검토할지 알려주시면 Alternatives와 Review Trigger에 추가하겠습니다.
