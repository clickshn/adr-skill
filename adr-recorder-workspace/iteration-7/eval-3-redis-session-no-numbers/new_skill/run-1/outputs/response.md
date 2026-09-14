`docs/adr/0002-move-session-store-to-redis.md`를 만들었습니다.

- **번호:** `docs/adr/`에 이미 ADR-0001(`0001-record-architecture-decisions.md`)이 있어서 기존 4자리 규칙대로 0002로 매겼습니다.
- **Status: Proposed** — 새로 내리는 결정이라서 이렇게 두었습니다. requirements.txt에는 `redis==5.0.8`이 이미 추가되어 있지만(미커밋) `app/session.py`는 아직 프로세스 메모리 dict 구현입니다.
- **Decision Source: Human** — 사용자가 직접 내린 결정이라 Confidence 필드는 뺐습니다.
- **Evidence 섹션 없음** — 실측 수치(부하, 세션 유실률 등)가 없어서 만들지 않았습니다. "서버 3대로 늘리면서 로그인이 풀린다"는 관찰은 Context에 적었습니다.
- **Alternatives** — 대화에 나온 "현행 유지(프로세스 메모리)"만 정리했습니다. 기각 사유는 "3대로 늘리면 인스턴스끼리 세션을 공유하지 못해 로그인이 풀린다"입니다. 다시 검토할 조건은 대화에 없어서 Recheck if 줄과 Review Trigger 섹션은 넣지 않았습니다.
- **Reversibility: Partial** — 코드 롤백은 간단합니다. 하지만 3대 구성을 유지하는 한 원래 문제가 다시 생기므로, 서버를 1대로 줄이지 않으면 실제로는 되돌리기 어렵다고 적었습니다.
- **남은 일(Implementation 체크리스트):**
  - `app/session.py`의 `get`/`put`을 Redis로 교체
  - Redis 접속 설정 추가(현재 저장소에 없음)
  - 세션 TTL 정의(현재 dict 구현에는 만료가 없음)
  - 여러 인스턴스에 걸친 세션 유지 테스트

`docs/adr/` 밖의 파일은 건드리지 않았습니다.
