ADR을 작성했습니다: `docs/adr/0002-session-store-redis.md`

기존 ADR이 `0001-record-architecture-decisions.md` 하나 있어서 그 번호 체계를 이어 **0002**로 만들었습니다.

작성 내용 요약:

- **Status: Proposed** — 새로 내리는 결정이라 `requirements.txt`에 이미 `redis==5.0.8`이 들어가 있어도 Proposed로 시작했습니다.
- **Context** — 세션이 `app/session.py`의 프로세스 전역 dict에만 있어서, 서버 3대로 늘리자 요청이 다른 서버로 가면 로그인이 풀리는 문제.
- **Alternatives** — 대화에 나온 "현행 유지(프로세스 메모리)"만 정리했고, 기각 사유는 말씀하신 그대로(서버 간 세션 비공유로 로그인 풀림) 적었습니다. 언급되지 않은 다른 대안은 추측해서 넣지 않았습니다.
- **Consequences / Risks** — Redis 단일 장애점, 조회당 네트워크 왕복, 그리고 기존 메모리 구현에는 없던 세션 TTL 정책을 새로 정해야 한다는 점을 적었습니다.
- **Reversibility** — `app/session.py`와 `requirements.txt`를 현재 HEAD(`ba84cb2`) 상태로 되돌리면 복구됩니다. Reversible: Yes / Migration Cost: Low.

측정 수치(지연, 세션 수 등)는 대화에 없어서 Evidence 섹션은 만들지 않았고, 재검토 조건도 명시된 게 없어 Recheck if / Review Trigger는 생략했습니다. 나중에 부하 테스트나 Redis 응답 시간 같은 실측값이 나오면 Evidence 섹션을 추가해 드릴 수 있습니다.

`docs/adr/` 밖의 파일은 건드리지 않았습니다.
