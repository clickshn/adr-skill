ADR을 작성했습니다: `docs/adr/0002-session-store-redis.md`

기존에 `docs/adr/0001-record-architecture-decisions.md`가 있어서 번호는 0002로 이어갔습니다.

**요약**

- **Status:** Proposed — 새로 내리는 결정이라 requirements.txt가 이미 바뀌어 있어도 Proposed로 시작했습니다.
- **Context:** `app/session.py`의 모듈 전역 `_sessions` 딕셔너리에 세션이 프로세스별로만 남아, 서버 3대 구성에서 로그인 때와 다른 서버로 요청이 가면 세션이 없어 로그인이 풀리는 문제.
- **Decision:** `get`/`put` 인터페이스는 유지하고 내부 구현만 Redis(`redis==5.0.8`)로 교체. 호출 측은 수정 없음.
- **Alternatives:** 대화에서 언급된 "프로세스 메모리 유지(현행)" 하나만 정리했고, 기각 사유는 말씀하신 3대 확장 시 로그인 유실 문제를 그대로 썼습니다.
- **Reversibility:** Yes. 롤백은 `app/session.py`를 69b2c22 시점 구현으로 되돌리고 redis 의존성 제거 — 다만 서버 1대 구성으로 함께 되돌려야 한다는 점을 적어뒀습니다.

**비워둔 섹션과 이유**

- **Evidence:** 실측 수치가 없어서 생성하지 않았습니다. "로그인이 풀린다"는 정성적 관찰은 Context에 넣었습니다. 세션 유실률이나 재로그인 발생 건수 같은 수치가 있으면 알려주세요, Evidence로 옮기겠습니다.
- **Review Trigger:** 재검토 조건이 대화에 없어서 Recheck if를 쓰지 않았고, 모을 내용이 없어 섹션도 만들지 않았습니다. "Redis 운영 부담이 커지면 재검토" 같은 조건이 있으면 추가해 드리겠습니다.
- **Confidence:** 결정 주체가 사람(Decision Source: Human)이라 생략했습니다.

참고로 스티키 세션이나 DB 세션 테이블, JWT 같은 다른 안을 함께 검토하셨다면 말씀해 주세요. 대화에 없던 대안을 추측해서 채우지는 않았습니다.

파일은 `docs/adr/` 안에만 생성했고 다른 파일은 건드리지 않았습니다.
