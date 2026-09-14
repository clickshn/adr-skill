`docs/adr/0002-redis-session-store.md`를 만들었습니다. 기존에 `0001-record-architecture-decisions.md`가 있어서 그 다음 번호와 자릿수를 따랐습니다.

정리한 내용:

- **Status: Proposed** — 새로 내리는 결정이라, `requirements.txt`에 redis가 이미 들어가 있어도 Proposed로 시작합니다.
- **Context** — 서버 3대 확장 후 로그인이 풀리는 현상, 그 원인이 `app/session.py`의 프로세스 내 `_sessions` 딕셔너리라는 점을 적었습니다.
- **Decision / Rationale** — `get`/`put` 시그니처를 유지한 채 내부 구현만 Redis로 교체하는 방향으로 썼습니다.
- **Consequences** — Redis 단일 장애점, TTL 정책 부재, 전환 배포 시 기존 세션 무효화(재로그인 발생)를 Risks에 담았습니다.
- **Reversibility** — 롤백은 `app/session.py` 원복 + redis 의존성 제거, 기준점 커밋은 `ba84cb2`로 적었습니다. Migration Cost는 Low로 봤습니다.

빼둔 섹션도 알려드립니다:

- **Evidence** — 벤치마크나 프로덕션 측정 수치가 없어서 만들지 않았습니다. "서버 3대에서 로그인이 풀린다"는 정성적 관찰은 Context에 넣었습니다.
- **Alternatives / Review Trigger** — 검토하신 다른 선택지가 대화에 안 나와서 추측으로 채우지 않았습니다.

**이 결정에서 기각한 대안과 근거를 알려주세요.** (예: 스티키 세션, DB 세션 테이블, JWT 등을 검토하셨다면 각각 왜 접었는지) 알려주시면 Alternatives 섹션을 채우고, 재검토 조건까지 주시면 Review Trigger도 함께 추가하겠습니다.
