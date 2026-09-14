`docs/adr/0002-session-store-redis.md`를 새로 만들었습니다. 기존에 `0001-record-architecture-decisions.md`가 있어서 그 다음 번호인 0002로 이어 붙였습니다.

정리한 내용:

- **Status: Proposed** — 새로 내린 결정이라 requirements.txt가 이미 바뀌어 있어도 Proposed로 시작합니다.
- **Context** — 세션이 `app/session.py`의 프로세스 내 딕셔너리에 있어 인스턴스별로 격리되고, 서버 3대 분산 시 로그인이 풀리는 문제.
- **Decision** — Redis(`redis==5.0.8`)를 공유 세션 저장소로 두고 `get`/`put` 구현만 교체.
- **Alternatives** — 현행 유지(프로세스 메모리)를 기각 사유(3대 확장 시 로그인 풀림)와 함께 적었습니다.
- **Reversibility** — 롤백은 `app/session.py`를 69b2c22에 들어있는 메모리 구현으로 되돌리고 requirements.txt에서 redis를 빼는 것. 해당 커밋이 실제로 `app/session.py`를 포함하는지 `git show --stat`으로 확인했습니다(최신 커밋 ba84cb2는 파일 변경이 없어 근거로 쓰지 않았습니다).

몇 가지는 일부러 비워뒀습니다:

- **Evidence** — 벤치마크나 실측 수치가 없어서 섹션을 만들지 않고, 3대 확장·로그인 풀림 같은 관찰은 Context에 넣었습니다.
- **Recheck if / Review Trigger** — 대화에 재검토 조건이 명시되지 않아 지어내지 않고 생략했습니다.

TTL·직렬화 형식, Redis 접속 설정처럼 아직 안 정해진 부분은 Implementation 체크리스트로 남겨뒀습니다. 내용 중 사실과 다른 부분이 있으면 알려주세요.
