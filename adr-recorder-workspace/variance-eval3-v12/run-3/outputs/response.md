ADR을 작성했습니다: `docs/adr/0002-redis-session-store.md`

기존에 `docs/adr/0001-record-architecture-decisions.md`가 있어서 번호를 0002로 이어갔고, 파일명도 기존 4자리 네이밍 규칙에 맞췄습니다.

정리한 내용:

- **Context**: 세션이 `app/session.py`의 모듈 전역 dict에 있어 프로세스 밖에서 공유되지 않고, 서버 3대 확장 후 다른 인스턴스로 요청이 가면 로그인이 풀리는 문제
- **Decision**: `redis==5.0.8`로 세션을 외부 공유 저장소에 두고, `get`/`put` 구현만 교체(호출부 시그니처 유지)
- **Alternatives**: 대화에 나온 "현행 유지(프로세스 메모리)"만 기각 사유와 함께 정리
- **Reversibility**: requirements.txt에서 redis 제거 + `app/session.py`를 메모리 구현(69b2c22에서 도입)으로 복구 — Reversible Yes / Migration Cost Low
- **Risks**: Redis가 단일 장애점이 되는 점, 직렬화 포맷·TTL 정책이 아직 없는 점(현재 메모리 구현엔 만료 개념이 없습니다)

판단이 필요했던 부분 두 가지:

1. **Status는 Proposed**로 뒀습니다. requirements.txt에 redis가 이미 추가돼 있지만 새로 내리는 결정이라 Proposed로 시작합니다. 실제로 반영·합의된 결정이면 Accepted로 바꾸시면 됩니다.
2. **Evidence 섹션은 넣지 않았습니다.** "로그인이 풀린다"는 정성적 관찰이라 Context에 적었고, 측정 수치(세션 조회 지연, 재로그인 발생률 등)가 생기면 그때 채우는 게 맞다고 봤습니다. 대화에 재검토 조건이 없어서 Recheck if / Review Trigger도 비워뒀습니다.

검토했다가 기각한 다른 대안이 있으면 알려주세요. Alternatives에 추가하겠습니다. 추측으로 채우지는 않았습니다.
