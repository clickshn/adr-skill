`docs/adr/0002-session-store-redis.md`를 새로 만들었습니다.

`docs/adr/`를 셸로 확인해 보니 기존 ADR이 `0001-record-architecture-decisions.md` 하나 있어서, 번호는 0002로 이어 붙이고 파일명도 기존 4자리 규칙을 따랐습니다.

**주요 판단**

- **Status는 Proposed**입니다. 기존 결정 로그를 옮기는 이관이 아니라 새로 내리는 결정이라, `requirements.txt`에 redis가 이미 추가돼 있어도 Proposed로 시작합니다.
- **Decision Source: Human** (사용자가 직접 내린 결정)이라 Confidence 필드는 생략했습니다.
- **Evidence 섹션은 만들지 않았습니다.** 벤치마크나 실측 수치가 없고, "서버를 3대로 늘리니 로그인이 풀린다"는 정성적 관찰이라 Context의 Problem에 적었습니다.
- **Alternatives**는 대화에 실제로 등장한 "프로세스 메모리 세션 유지(현행)" 하나만 적었습니다. 재검토 조건이 대화에 없어서 `Recheck if` 줄은 생략했고, Review Trigger는 모을 `Recheck if`가 하나도 없어 섹션을 만들지 않았습니다.
- **Rollback 기준 커밋은 83bb4e5**로 적었습니다. HEAD인 `bd074f7`("feat: 로그인/로그아웃 API")은 `git show --stat`으로 확인해 보니 파일 변경이 하나도 없는 빈 커밋이라, `app/session.py`를 실제로 담고 있는 `83bb4e5`를 인용했습니다.

**되묻습니다**

이 결정에서 Redis 말고 검토했다가 기각한 대안(예: DB 세션 테이블, sticky session, JWT 기반 무상태 인증 등)과 그 근거를 알려주세요. 대화에 근거가 없어 추측으로 채우지 않았습니다. 알려주시면 Alternatives에 추가하겠습니다.

참고로 `docs/adr/` 밖의 파일(`requirements.txt`, `app/session.py`)은 건드리지 않았습니다. `app/session.py`의 실제 Redis 전환은 ADR의 Implementation 체크리스트로만 남겨뒀습니다.
