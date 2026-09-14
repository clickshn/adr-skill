`docs/adr/0002-session-store-redis.md`를 만들었습니다.

기존 `docs/adr/`에 `0001-record-architecture-decisions.md`가 있어서, 그 4자리 번호 규칙을 이어 **0002**로 붙였습니다.

작성 내용 요약:

- **Status: Proposed** — requirements.txt에 `redis==5.0.8`이 이미 추가돼 있지만, 새로 내리는 결정이라 Proposed로 시작했습니다. 구현 후 합의되면 Accepted로 바꾸시면 됩니다.
- **Decision Source: Human** (직접 결정하신 내용이라 Confidence 필드는 생략)
- **Context** — 세션이 `app/session.py`의 `_sessions` 딕셔너리에만 있어 프로세스 밖으로 공유되지 않고, 서버 3대 분산 시 로그인이 풀리는 문제로 정리했습니다.
- **Alternatives** — 말씀하신 "현행 유지(프로세스 메모리)"만 기각 사유와 함께 적었습니다. 언급되지 않은 다른 대안(sticky session, DB 세션 등)은 추측해서 채우지 않았습니다.
- **Reversibility** — 롤백은 `app/session.py`를 메모리 구현(커밋 `69b2c22`)으로 되돌리고 requirements.txt에서 redis를 빼는 것으로, Migration Cost는 Low로 봤습니다.

실측 수치가 없어 Evidence 섹션은 만들지 않았고, 재검토 조건이 대화에 없어서 Recheck if / Review Trigger도 넣지 않았습니다.

참고로 구현 체크리스트에 **세션 직렬화 방식과 TTL 정책**을 넣어뒀습니다. 현재 `get`/`put`은 dict를 그대로 주고받아서 Redis로 옮길 때 이 두 가지를 정하셔야 합니다. 재검토 조건이나 기각한 다른 대안이 있으면 알려주시면 ADR에 반영하겠습니다.
