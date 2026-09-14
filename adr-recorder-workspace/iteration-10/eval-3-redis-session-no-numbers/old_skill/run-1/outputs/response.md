ADR을 작성했습니다: `docs/adr/0002-move-session-store-to-redis.md`

- **번호:** `docs/adr/`에 이미 `0001-record-architecture-decisions.md`가 있어서, 같은 4자리 형식을 따라 ADR-0002로 만들었습니다.
- **Status:** Proposed. requirements.txt는 이미 바뀌었지만, 새로 내린 결정이라 Proposed로 시작합니다.
- **Context/Decision:** 서버 3대 환경에서 프로세스 메모리 세션(`app/session.py`의 dict) 때문에 로그인이 풀리는 문제와, 세션을 Redis(`redis==5.0.8`)로 옮기는 결정을 기록했습니다. `get`/`put` 인터페이스는 그대로 두고 내부 저장소만 바꾸는 방향입니다.
- **Alternatives:** 대화에 나온 대안인 "현행 유지(프로세스 메모리)"만 넣었고, 기각 사유는 말씀하신 로그인 풀림 문제입니다. 다시 검토할 조건은 대화에 없어서 Recheck if와 Review Trigger는 뺐습니다.
- **Evidence:** 측정 수치가 없어서 섹션을 만들지 않았습니다.
- **Implementation:** requirements.txt 반영은 완료로 표시했습니다. `app/session.py`는 아직 dict 구현이라 미완료로 남겼습니다.
- **Risks:** 코드를 보고 확인한 내용도 적었습니다. Redis가 단일 장애점이 된다는 점, 전환할 때 기존 세션이 옮겨지지 않아 한 번 재로그인이 필요하다는 점, 현재 코드에 세션 만료 로직이 없다는 점입니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.
