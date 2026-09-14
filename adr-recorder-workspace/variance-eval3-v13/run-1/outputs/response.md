`docs/adr/0002-session-store-redis.md` 를 만들었습니다.

기존 ADR이 `0001-record-architecture-decisions.md` 하나 있어서 번호는 0002로 이어 붙였고, 파일명 자릿수도 기존 규칙(4자리)에 맞췄습니다.

주요 내용:

- **Status: Proposed** — 새로 내리는 결정이라 requirements.txt가 이미 바뀌어 있어도 Proposed로 시작합니다. 구현이 끝나면 Accepted로 바꾸세요.
- **Context** — 서버 3대 확장 시 세션이 프로세스에 갇혀 로그인이 풀리는 문제. `app/session.py`를 확인해 전역 dict(`_sessions`) 기반 구현임을 근거로 적었습니다(69b2c22에서 도입된 코드).
- **Alternatives** — 대화에서 언급된 "현행 유지(프로세스 메모리)"만 정리했습니다. 기각 사유는 말씀하신 로그인 풀림 문제 그대로입니다.
- **Reversibility** — 되돌리는 방법은 저장소에서 확인해서 적었습니다(session.py를 dict 구현으로 복원 + requirements.txt에서 redis 제거).

두 가지 알려드릴 점:

- **Evidence 섹션은 넣지 않았습니다.** 로그인 풀림은 관찰된 현상이지 측정 수치가 아니라서 Context에 적었습니다. 재현율이나 세션 유실 건수 같은 수치가 있으면 알려주세요, Evidence로 옮기겠습니다.
- **Review Trigger도 만들지 않았습니다.** 재검토 조건(Recheck if)이 대화에 없어서 지어내지 않았습니다. "Redis 운영 부담이 커지면 재검토" 같은 조건을 정해두셨다면 추가하겠습니다.

문서 안에 `app/session.py` 교체와 TTL 설정을 Implementation 체크리스트로 남겨뒀습니다. 파일은 `docs/adr/` 안에만 만들었고 다른 파일은 건드리지 않았습니다.
