ADR을 작성했습니다: `docs/adr/0002-move-session-store-to-redis.md`

- **번호:** docs/adr/에 기존 `0001-record-architecture-decisions.md`가 있어 다음 번호인 ADR-0002로 만들었고, 기존 파일의 4자리 번호 형식을 그대로 따랐습니다.
- **Status:** Proposed. requirements.txt에 redis가 이미 들어가 있어도 새로 내린 결정이라 Proposed로 시작합니다. `app/session.py`는 아직 dict 기반이라 Implementation 체크리스트에는 redis 추가만 완료로 표시했습니다.
- **내용:** 서버 3대 환경에서 세션이 프로세스 메모리에만 있어 로그인이 풀리는 문제를 배경으로, 공유 저장소인 Redis(`redis==5.0.8`)로 옮기는 결정을 정리했습니다.
- **Alternatives:** 대화에 나온 대안인 "현행 유지(프로세스 메모리)"만 넣었고, 기각 사유는 말씀하신 로그인 풀림 문제입니다. 말씀하지 않은 대안은 추가하지 않았습니다.
- **생략한 섹션:**
  - Evidence: 실측 수치가 없어서 뺐습니다.
  - Confidence: 결정 주체가 사람이라 뺐습니다.
  - Review Trigger: 말씀하신 재검토 조건이 없어서 뺐습니다.
- **Reversibility:** `app/session.py`가 `get`/`put` 두 함수뿐이라 되돌리는 비용은 Low로 적었습니다. 되돌리면 Redis에 있던 세션이 사라지고 로그인 풀림 문제가 다시 생긴다는 점도 함께 적었습니다.

docs/adr/ 밖의 파일(requirements.txt, app/session.py 등)은 건드리지 않았습니다.
