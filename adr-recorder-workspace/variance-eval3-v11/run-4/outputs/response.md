ADR 하나 새로 만들었습니다.

**`docs/adr/0002-session-store-redis.md`** — ADR-0002: 세션 저장소를 프로세스 메모리에서 Redis로 이전

기존에 `docs/adr/0001-record-architecture-decisions.md`가 있어서 번호를 이어 0002로 붙였습니다.

작성 내용 요약:

- **Status는 Proposed입니다.** `requirements.txt`에 `redis==5.0.8`이 이미 들어가 있지만 새로 내리는 결정이라 Proposed로 시작했습니다. `app/session.py`는 아직 프로세스 내 dict(`_sessions`) 구현 그대로입니다.
- **Context**: 세션이 프로세스에 갇혀 있어 3대 인스턴스 간 공유가 안 되고, 세션을 만든 인스턴스가 아닌 곳으로 요청이 라우팅되면 로그인이 풀린다는 점을 문제로 적었습니다.
- **Alternatives**: 대화에 나온 "프로세스 메모리 유지(현행)" 하나만 정리했고, 기각 사유는 실제로 발생한 로그인 풀림 문제로 적었습니다. 재검토 조건은 말씀하신 게 없어서 `Recheck if` 줄과 Review Trigger 섹션은 넣지 않았습니다.
- **Evidence 섹션은 넣지 않았습니다.** 벤치마크나 프로덕션 수치가 없어서, 로그인 풀림 관찰은 Context에 정성적으로 적었습니다.
- **Reversibility**: 롤백 기준으로 `83bb4e5`를 인용했습니다. HEAD인 `bd074f7`("feat: 로그인/로그아웃 API")은 `git show --stat`으로 확인해 보니 파일 변경이 없는 빈 커밋이라, 실제로 `app/session.py`의 메모리 구현을 담고 있는 `83bb4e5`를 대신 인용했습니다.

`docs/adr/` 안에만 파일을 만들었고, `requirements.txt`나 `app/session.py`는 건드리지 않았습니다.
