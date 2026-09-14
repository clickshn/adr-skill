`docs/adr/0002-move-session-store-to-redis.md`에 ADR을 작성했습니다.

기존에 `0001-record-architecture-decisions.md`가 있어서 번호는 0002로 이어 붙였고, 파일명도 기존 4자리 규칙을 따랐습니다.

정리한 내용:

- **Context** — 3대 인스턴스로 늘리면서 세션이 프로세스별로 분리돼 다른 인스턴스로 요청이 가면 로그인이 풀리는 문제. `app/session.py`가 실제로 프로세스 내 딕셔너리(`_sessions`)로 구현돼 있는 것을 확인해서 함께 적었습니다.
- **Decision** — `get`/`put` 시그니처는 유지하고 내부 구현만 Redis로 교체. requirements.txt에 `redis==5.0.8`이 추가된 것은 diff로 확인했고, `app/session.py`는 아직 딕셔너리 구현이라는 현재 상태도 명시했습니다.
- **Alternatives** — 말씀하신 현행(프로세스 메모리) 유지를 기각 사유(3대 확장 시 로그인 풀림)와 함께 정리했습니다.
- **Consequences / Risks** — Redis 단일 장애점, 전환 시점의 기존 세션 소실로 인한 재로그인, 직렬화·TTL 정책 필요.
- **Reversibility** — Yes. 되돌리려면 `app/session.py`를 딕셔너리 구현으로 복구하고 requirements.txt에서 redis를 제거(서버 1대 축소가 전제).

몇 가지 참고하실 점:

- **Status는 Proposed입니다.** requirements.txt가 이미 바뀌어 있어도, 새로 내리는 결정은 Proposed로 시작하는 것이 이 문서의 규칙입니다. 구현·배포까지 끝나면 Accepted로 바꾸시면 됩니다.
- **Evidence 섹션은 넣지 않았습니다.** "로그인이 풀린다"는 관찰은 있지만 측정 수치(발생률, 지연 등)가 없어서 Context에 서술로만 적었습니다. 수치가 있으면 알려주시면 Evidence로 옮기겠습니다.
- **Review Trigger 섹션도 없습니다.** 재검토 조건이 대화에 없어서 지어내지 않았습니다. "Redis 운영 부담이 커지면 재검토" 같은 조건이 실제로 있다면 추가해 드릴게요.
- HEAD 커밋(`ba84cb2`)은 파일 변경이 없는 빈 커밋이라 근거로 인용하지 않았습니다.

Implementation 체크리스트에 TTL 설정, 접속 정보 환경변수화, 3대 환경 세션 유지 테스트, 모니터링을 넣어 뒀습니다. 이어서 `app/session.py`의 Redis 전환 구현도 해드릴까요?
