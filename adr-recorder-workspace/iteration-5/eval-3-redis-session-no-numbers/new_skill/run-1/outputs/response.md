ADR을 작성했습니다: `docs/adr/0002-move-session-store-to-redis.md`

**번호:** `docs/adr/`에 이미 `0001-record-architecture-decisions.md`가 있어서, 같은 4자리 번호 규칙에 맞춰 **ADR-0002**로 만들었습니다.

**내용 요약**
- **Context:** 지금 세션은 `app/session.py`의 전역 dict(`_sessions`)에 저장됩니다. 그래서 서버를 3대로 늘리자, 로그인을 처리한 서버와 다른 서버로 요청이 가면 로그인이 풀립니다.
- **Decision:** `get`/`put` 인터페이스는 그대로 두고 저장소만 Redis(`redis==5.0.8`)로 바꿔, 앱 서버가 세션 상태를 갖지 않게 합니다.
- **Consequences:** Redis가 멈추면 전체 로그인이 안 되는 단일 장애점이 되는 점, 전환 배포 때 기존 세션이 사라져 한 번 재로그인이 필요한 점, 직렬화와 TTL 설정이 필요한 점을 적었습니다.
- **Implementation / Reversibility:** `app/session.py` 교체 체크리스트와 롤백 방법(dict 구현 복원, redis 의존성 제거)을 넣었습니다.

**작성 시 판단한 점**
- 직접 결정하신 내용이라 Decision Source는 `Human`으로 적었고, 그래서 Confidence는 생략했습니다.
- 대화에 측정 수치(로그인 풀림 빈도, 지연 등)가 없어서 **Evidence** 섹션은 만들지 않았습니다.
- 기각한 대안을 말씀하지 않으셔서 **Alternatives**와 **Review Trigger** 섹션은 비워 두었습니다. 추측으로 채우지 않았습니다.
- Status는 템플릿 기본값인 `Proposed`로 두었습니다. 이미 확정된 결정이면 `Accepted`로 바꾸시면 됩니다.

이 결정에서 기각한 대안과 근거를 알려주세요. 예를 들어 로드밸런서 스티키 세션, DB(SQLAlchemy) 세션 테이블, 서명 쿠키/JWT 같은 방식을 검토하셨다면, 왜 선택하지 않았는지 알려주시면 Alternatives와 Review Trigger 섹션을 채워 넣겠습니다.
