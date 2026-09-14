`docs/adr/0002-move-session-store-to-redis.md`를 만들었습니다.

- **번호:** docs/adr/에 `0001-record-architecture-decisions.md`가 이미 있어서, 같은 4자리 형식을 따라 0002로 정했습니다.
- **Status: Proposed:** requirements.txt에 `redis==5.0.8`은 이미 들어가 있지만, 이번에 새로 내리는 결정이라 Proposed로 시작합니다.
- **Confidence, Evidence:** 직접 내리신 결정이라 Decision Source를 Human으로 두었고, 그래서 Confidence는 생략했습니다. 측정 수치가 없어서 Evidence 섹션도 넣지 않았습니다.
- **Alternatives:** 대화에 나온 "현행 유지(프로세스 메모리)"만 넣었습니다. 기각 사유는 "서버 3대에서 로그인이 풀린다"입니다. 재검토 조건은 말씀하신 게 없어서 Recheck if와 Review Trigger는 넣지 않았습니다.
- **Reversibility: Partial:** 커밋 `0c08f5e`의 dict 구현으로 코드를 되돌리기는 쉽습니다. 하지만 서버 3대 구성에서는 같은 문제가 다시 생깁니다.

참고:
- `app/session.py`는 아직 dict 기반 그대로입니다. 그래서 Redis로 바꾸는 작업, 세션 직렬화, 세션 만료 정책(지금은 만료가 없음)은 Implementation 체크리스트에 올려두었습니다.
- 최근 커밋 `5a76edd`("로그인/로그아웃 API")는 변경된 파일이 없는 빈 커밋이라 근거로 인용하지 않았습니다.
- docs/adr/ 밖의 파일은 수정하지 않았습니다.
