ADR을 작성했습니다: `docs/adr/0002-session-store-redis.md`

**번호:** `docs/adr/`에 이미 `0001-record-architecture-decisions.md`가 있어서 다음 번호인 0002를 붙였습니다. 파일명과 제목은 기존 4자리 형식(`ADR-0002`)을 따랐습니다.

**작성한 내용**
- **Status:** Proposed. requirements.txt는 이미 바뀌었지만 새로 내리는 결정이라 Proposed로 시작했습니다.
- **Context:** `app/session.py`는 세션을 모듈 전역 dict(`_sessions`)에 저장합니다. 그래서 서버를 3대로 늘리면 다른 서버로 간 요청에서 로그인이 풀립니다.
- **Decision:** Redis(`redis==5.0.8`)를 세 서버가 함께 쓰는 세션 저장소로 씁니다. `get`/`put`을 Redis 기반으로 바꿔야 합니다.
- **Alternatives:** 대화에 나온 대안은 "프로세스 메모리 유지(현행)" 하나라서 그것만 적었습니다. 기각 사유는 말씀하신 "서버 3대에서 로그인이 풀림"입니다.
- **Risks:** Redis가 단일 장애점이 됩니다. 또 현재 dict 구현에는 세션 만료가 없어서 그대로 옮기면 Redis에 키가 계속 쌓입니다. 이 점을 적어 두었습니다.
- **Implementation:** requirements.txt 변경은 완료로 체크했습니다. `app/session.py` 교체, 테스트, 모니터링, 설정 추가는 남은 작업으로 두었습니다.

**넣지 않은 섹션**
- **Evidence:** 측정 수치가 없어서 뺐습니다. 사용자가 직접 내린 결정(Human)이라 Confidence도 없습니다.
- **Recheck if / Review Trigger:** 대화에 재검토 조건이 없어서 둘 다 뺐습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다. `app/session.py`는 아직 dict 기반 그대로입니다.
