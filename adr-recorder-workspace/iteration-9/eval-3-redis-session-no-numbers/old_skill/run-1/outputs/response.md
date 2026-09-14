`docs/adr/0002-session-store-redis.md`에 ADR을 만들었습니다.

- **번호:** `docs/adr/`에 이미 `0001-record-architecture-decisions.md`가 있습니다. 그 파일이 쓰는 4자리 번호 형식을 따라 **ADR-0002**로 붙였습니다.
- **Status: Proposed.** `requirements.txt`에 `redis==5.0.8`이 이미 들어가 있지만 새로 내리는 결정이라 Proposed로 시작했습니다. `app/session.py`는 아직 dict 기반이라서 교체 작업은 Implementation 체크리스트에 남겨 두었습니다.
- **Decision Source: Human.** 직접 내리신 결정이라 Confidence 필드는 뺐습니다.
- **만들지 않은 섹션:**
  - Evidence: 측정 수치가 없습니다.
  - Alternatives, Review Trigger: 대화에서 검토한 대안이 나오지 않았습니다.
- **Reversibility:** 되돌릴 수는 있습니다(Yes, Migration Cost Low). 다만 서버 3대 구성에서 되돌리면 로그인 풀림 문제가 다시 생깁니다.

`docs/adr/` 밖의 파일(`app/session.py`, `requirements.txt` 등)은 건드리지 않았습니다.

이 결정에서 기각한 대안과 근거를 알려주세요. 알려주시면 Alternatives와 Review Trigger 섹션을 채우겠습니다.
