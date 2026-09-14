ADR을 새로 작성했습니다.

**생성:** `docs/adr/0002-redis-session-store.md` — ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

- `docs/adr/`를 셸로 확인해 기존 ADR이 `0001-record-architecture-decisions.md` 하나뿐인 것을 보고 다음 번호인 **0002**로 붙였습니다(파일명 자릿수는 기존 컨벤션에 맞춤).
- **Status는 Proposed**입니다. `requirements.txt`에 `redis==5.0.8`이 이미 추가되어 있지만, 기존 결정 로그를 이관한 것이 아니라 새로 내리는 결정이므로 코드가 먼저 바뀌었더라도 Proposed로 시작합니다.
- Decision Source는 Human(직접 말씀하신 결정)이라 Confidence 필드는 생략했습니다.
- 측정 수치가 없어 **Evidence 섹션은 만들지 않았고**, "서버 3대 확장 후 로그인이 풀린다"는 정성적 관찰은 Context의 Problem에 넣었습니다.
- Alternatives에는 대화에 등장한 대안인 **"프로세스 메모리 유지(현행)"** 하나만 정리했습니다. Memcached나 sticky session 같은 대안은 언급되지 않아 추측으로 채우지 않았습니다.
- 재검토 조건이 대화에 명시되지 않아 **Recheck if 줄과 Review Trigger 섹션은 생성하지 않았습니다**(기각 사유를 뒤집은 조건은 지어낸 것으로 보고 쓰지 않았습니다).
- 근거로 참고한 것: `git diff HEAD`의 `requirements.txt` 변경(`+redis==5.0.8`), 현재 메모리 딕셔너리 구현인 `app/session.py`, HEAD 커밋 `bd074f7`(롤백 기준점 표시 용도).

이 결정에서 따로 검토했다가 기각한 다른 대안(예: DB 세션 테이블, sticky session, Memcached)과 그 근거가 있으면 알려주세요. Alternatives에 추가하겠습니다. 재검토 조건(예: "Redis 운영 부담이 커지면")이 있다면 Review Trigger도 같이 채우겠습니다.

참고로 `docs/adr/` 밖의 파일(`requirements.txt`, `app/session.py`)은 건드리지 않았습니다.
