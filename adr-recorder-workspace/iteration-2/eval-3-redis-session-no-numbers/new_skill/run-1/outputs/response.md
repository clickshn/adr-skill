세션 저장소 결정을 `docs/adr/0002-move-session-store-to-redis.md`에 **ADR-0002**로 작성했습니다.

- **번호:** `docs/adr/`에 ADR-0001이 이미 있어서 이 결정을 0002로 매겼습니다.
- **Status / Decision Source:** 새로 내린 결정이라 Status는 `Proposed`, 직접 내리신 결정이라 Decision Source는 `Human`으로 적었습니다. Human이면 Confidence 필드는 넣지 않습니다.
- **Context:** `app/session.py`는 모듈 전역 dict에 세션을 저장합니다. 그래서 서버를 3대로 늘리자 로그인하지 않은 다른 서버로 요청이 가면 세션을 찾지 못합니다.
- **Decision:** `get`/`put` 인터페이스는 그대로 두고, 내부 저장소만 Redis(`redis==5.0.8`)로 바꾸는 방향입니다. 변경은 `app/session.py` 한 파일에서 끝납니다.
- **Consequences:** 다음 위험 요소를 적어 두었습니다.
  - Redis가 멈추면 세 서버 모두 로그인이 안 됩니다(단일 장애점).
  - 전환하는 배포 직후 로그인해 있던 사용자는 한 번 로그아웃됩니다.
  - Redis 영속성 설정에 따라 Redis 재시작 시 세션이 사라질 수 있습니다.
  - Redis 접근 제어가 약하면 세션을 탈취당할 수 있습니다.
- **Implementation:** `app/session.py`는 아직 dict 구현 그대로입니다. 그래서 세션 모듈 교체, 테스트, 모니터링, Redis 접속 설정 분리를 체크리스트로 넣었습니다.
- **Evidence:** 제공된 실측 수치가 없어서 섹션을 만들지 않았습니다. 로그인이 풀린 현상은 Context에 적었습니다.

**Alternatives 섹션은 비워 두지 않고 아예 뺐습니다.** 대화에 검토했다가 버린 대안의 이유가 없어서, 추측해서 채우지 않았습니다. 그래서 대안의 Recheck if를 모아 만드는 Review Trigger 섹션도 없습니다.

이 결정에서 기각한 대안과 근거를 알려주세요. 예를 들어 로드밸런서 sticky session, 기존 SQL DB에 세션 테이블 두기, JWT 같은 stateless 토큰 방식을 검토했는지, 검토했다면 왜 뺐는지요. 알려주시면 Alternatives와 Review Trigger 섹션을 채워 넣겠습니다.
