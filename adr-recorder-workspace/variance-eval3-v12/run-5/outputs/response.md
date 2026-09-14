ADR 작성했습니다: `docs/adr/0002-session-store-redis.md`

기존에 `0001-record-architecture-decisions.md`가 있어서 그 4자리 번호 규칙을 이어 **ADR-0002**로 만들었습니다.

**주요 내용**
- **Status:** Proposed — 새로 내리는 결정이라, `requirements.txt`에 이미 redis가 들어가 있어도 Proposed로 시작했습니다.
- **Context:** `app/session.py`의 모듈 전역 dict(`_sessions`)에 세션을 두고 있어, 3대 중 다른 인스턴스로 요청이 가면 세션이 없어 로그인이 풀리는 상황을 문제로 정리했습니다.
- **Decision:** Redis(`redis==5.0.8`)를 공유 세션 저장소로 두고, `get`/`put` 시그니처는 유지한 채 구현만 교체.
- **Alternatives:** 말씀하신 범위에서 확인된 대안은 "현행 유지(프로세스 메모리)" 하나뿐이라 그것만 적었고, 기각 사유는 3대 확장 후 실제로 로그인이 풀렸다는 점으로 썼습니다.
- **Consequences/Risks:** Redis 단일 장애점, 전환 시점 기존 세션 유실(전원 재로그인), 세션 조회당 네트워크 왕복을 적었습니다.
- **Reversibility:** Yes / Rollback은 `app/session.py`를 현재 HEAD(ba84cb2) 시점 메모리 구현으로 되돌리고 requirements에서 redis 제거.

**비워 둔 곳**
- **Evidence**: 지연시간·세션 수 같은 실측 수치가 없어서 섹션을 만들지 않았습니다. "서버 3대" 같은 정성적 사실은 Context에 넣었습니다.
- **Review Trigger / Recheck if**: 재검토 조건이 대화에 없어 지어내지 않고 비워 뒀습니다.

Memcached, DB 세션 테이블, 스티키 세션처럼 검토했다가 접은 안이 있으면 알려주세요. Alternatives에 근거와 함께 채워 넣겠습니다. 재로그인 없이 전환하려면 이중 쓰기 단계가 필요한데, 그 계획도 필요하면 Implementation에 반영할게요.

참고로 `docs/adr/` 밖의 파일(`app/session.py`, `requirements.txt` 등)은 건드리지 않았습니다.
