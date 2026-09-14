ADR을 작성했습니다: `docs/adr/0002-redis-session-store.md`

**번호**: `docs/adr/`를 셸로 확인해 보니 `0001-record-architecture-decisions.md`가 이미 있어서, 같은 4자리 규칙을 따라 **0002**로 이어 붙였습니다.

**작성 내용 요약**
- **Status: Proposed** — `requirements.txt`에 redis가 이미 추가돼 있지만, 이건 기존 결정 로그를 옮겨 적은 게 아니라 새로 내리는 결정이라 Proposed로 시작했습니다.
- **Context** — `app/session.py`가 프로세스 메모리 `dict`(`_sessions`)를 쓰고 있고, 3대로 늘린 뒤 세션을 만든 인스턴스가 아닌 곳으로 요청이 가면 로그인이 풀린다는 점을 문제로 적었습니다.
- **Decision / Rationale / Consequences / Implementation / Reversibility** — 교체 지점이 `get`/`put` 두 함수뿐이라 롤백은 Low로 봤습니다.

**일부러 비워둔 것**
- **Evidence 섹션 없음** — 벤치마크·실측 수치가 대화에 없어서 섹션 자체를 만들지 않았습니다. "3대로 늘린 뒤 로그인이 풀린다"는 정성적 관찰이라 Context에 넣었습니다.
- **Alternatives는 '현행 유지' 하나만** — 대화에 나온 대안이 그것뿐입니다. sticky session, DB 세션, JWT 같은 건 언급이 없어서 추측으로 채우지 않았습니다.
- **Review Trigger 없음** — Alternatives에 재검토 조건(Recheck if)이 하나도 없어서, 빈 섹션을 만들지 않았습니다.

**확인 중 발견한 것**: HEAD 커밋 `bd074f7`("feat: 로그인/로그아웃 API")은 `git show --stat`으로 보니 변경 파일이 없는 빈 커밋이었습니다. 그래서 프로세스 메모리 세션 저장소의 출처로는 실제로 `app/session.py`를 담고 있는 `83bb4e5`를 인용하고, `bd074f7`은 롤백 기준점(현재 위치)으로만 적었습니다.

하나만 여쭤볼게요: Redis 말고 검토했다가 기각한 대안(예: sticky session, DB 세션 테이블)이 있었다면 그 근거를 알려주세요. Alternatives에 추가하겠습니다. 재검토 조건(예: "Redis 운영 부담이 커지면 다시 본다")도 있으면 같이 주시면 Review Trigger를 채우겠습니다.
