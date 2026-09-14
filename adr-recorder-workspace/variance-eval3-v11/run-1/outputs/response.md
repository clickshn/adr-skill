`docs/adr/0002-move-session-store-to-redis.md` 를 새로 만들었습니다.

**ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전**

- 번호: 기존 ADR이 `0001-record-architecture-decisions.md` 하나뿐이라 다음 번호인 `0002`로 붙였습니다.
- Status: `Proposed`. requirements.txt에 redis가 이미 추가돼 있지만, 기존 결정 로그 이관이 아니라 새로 내리는 결정이라 Proposed로 시작했습니다.
- Context: `app/session.py`가 모듈 전역 dict에 세션을 들고 있어 프로세스 간 공유가 안 되고, 서버 3대 구성에서 다른 인스턴스로 라우팅되면 로그인이 풀린다는 점을 문제로 적었습니다.
- Decision/Rationale: 세션을 3대가 공유하는 외부 Redis로 옮기고 `get`/`put` 인터페이스는 유지하는 방향으로 정리했습니다.
- Evidence 섹션은 측정 수치가 없어 만들지 않았고, 관찰된 증상은 Context에 넣었습니다.
- Alternatives는 대화에 나온 "현행 유지(프로세스 메모리)" 하나만 적었습니다. 재검토 조건이 언급되지 않아 Recheck if와 Review Trigger는 넣지 않았습니다.
- 스킬 범위대로 `docs/adr/` 안에만 파일을 만들었고, `requirements.txt`나 `app/session.py`는 건드리지 않았습니다.

이 결정에서 기각한 대안과 근거를 알려주세요. (현행 유지 외에 검토했다가 접은 선택지가 있으면 그 사유까지 알려주시면 Alternatives에 추가하겠습니다.)
