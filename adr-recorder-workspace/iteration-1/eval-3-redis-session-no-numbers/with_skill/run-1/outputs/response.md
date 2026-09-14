ADR을 작성했어요: `docs/adr/001-redis-session-store.md`

**요약**
- **결정:** `app/session.py`의 프로세스 메모리 dict 세션 저장소를 Redis(`redis==5.0.8`)로 옮겨 서버 3대가 세션을 공유하도록 함
- **Status:** Proposed / **Decision Source:** Human (말씀하신 결정이라 Confidence는 생략)
- **Context:** 서버 3대로 늘리면서 다른 인스턴스로 요청이 가면 세션을 못 찾아 로그인이 풀리는 문제
- **Consequences/Risks:** Redis가 단일 장애점이 됨, 전환 시 기존 세션 유실(1회 재로그인), 요청마다 네트워크 왕복 추가
- **Reversibility:** Yes / Migration Cost Low (세션 모듈이 `get`/`put` 두 함수뿐이라 되돌리기 쉬움)

**코드에서 찾은 것:** 지금 `app/session.py`에는 세션 만료나 삭제 로직이 없어요. 그대로 Redis로 옮기면 키가 무기한 쌓이니까, Implementation 체크리스트에 TTL 설정과 로그아웃용 삭제 함수를 넣어뒀어요.

**비워둔 섹션:** 대화에서 확인된 실측 수치나 검토한 대안이 없어서 Evidence, Alternatives, Review Trigger 섹션은 넣지 않았어요. 추측해서 채우지 않았습니다.

이 결정에서 기각한 대안과 수치적 근거를 알려주세요. 예를 들면 로드밸런서 sticky session, DB(SQLAlchemy) 테이블 세션, JWT 같은 무상태 토큰을 검토했는지, 로그인 풀림 빈도나 세션 조회 지연 같은 수치가 있는지 알려주시면 Alternatives, Evidence, Review Trigger를 채워 넣을게요.
