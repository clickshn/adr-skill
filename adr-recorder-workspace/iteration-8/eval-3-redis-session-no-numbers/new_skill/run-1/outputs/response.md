`docs/adr/0002-redis-session-store.md`에 ADR-0002 "세션 저장소를 프로세스 메모리에서 Redis로 이전"을 작성했습니다.

- **번호:** `docs/adr/`에 이미 `0001-record-architecture-decisions.md`가 있어서 다음 번호인 0002를 붙였습니다. 파일명과 제목도 기존 4자리 형식(`0002-...`, `ADR-0002`)을 따랐습니다.
- **Status:** 새로 내린 결정이라 `Proposed`로 두었습니다. `requirements.txt`에 `redis==5.0.8`가 이미 추가되어 있어도 마찬가지입니다.
- **근거:** "서버를 3대로 늘리자 로그인이 풀린다"는 문제를 Context와 Rationale에 적었습니다. 코드를 보면 원인이 확인됩니다. 세션이 `app/session.py`의 모듈 전역 dict에 저장되어 프로세스마다 따로 존재합니다.
- **Evidence:** 측정 수치가 없어서 섹션을 만들지 않았습니다. 사용자가 직접 내린 결정(Decision Source: Human)이라 Confidence도 생략했습니다.
- **Alternatives:** 대화에 나온 대안인 "프로세스 메모리 유지(현행)"만 정리했습니다. 이 대안을 기각한 사유는 로그인이 풀리는 문제로 대화에 나와 있습니다. 재검토 조건은 언급되지 않아서 Recheck if와 Review Trigger는 넣지 않았습니다.
- **Implementation:** 체크리스트를 달았습니다. `requirements.txt`에 redis를 추가한 것은 완료로 표시했습니다. `app/session.py`는 아직 dict 기반이라 Redis로 교체하는 작업을 남은 항목으로 두었습니다.
- **Reversibility:** 롤백 방법을 적었습니다. 되돌리면 Redis에 있던 세션은 사라져 사용자가 한 번 다시 로그인해야 합니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.
