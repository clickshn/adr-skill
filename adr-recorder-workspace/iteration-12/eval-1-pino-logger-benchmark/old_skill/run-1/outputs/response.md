ADR을 새로 만들었습니다.

**생성 파일:** `docs/adr/ADR-003-pino-logger.md`

기존 ADR이 001, 002까지 있어서 **003**으로 이어 붙였습니다.

**작성 내용 요약**

- **Status: Proposed** — package.json이 이미 바뀌어 있어도, 기존 결정 로그 이관이 아닌 새 결정이라 Proposed로 시작합니다. 실제로 반영하기로 확정되면 Accepted로 올려주세요.
- **Decision Source: Human** (직접 내린 결정이라 Confidence 필드는 생략)
- **Evidence** — autocannon 측정치를 그대로 넣었습니다: p99 38ms → 21ms, 처리량 8.2k → 11.5k req/s.
- **Alternatives** — winston 유지(현행 유지)와 bunyan 두 가지. bunyan은 "마지막 릴리스 3년 전"을 기각 사유로, 말씀하신 "유지보수 재개되면 재검토"를 Recheck if에 넣었고 Review Trigger로도 모았습니다.
- **Reversibility** — Yes / Migration Cost Low. 롤백은 package.json 되돌리기 + `src/logger.js`를 f6a7269 시점 winston 구성으로 복원하는 선에서 끝납니다(데이터 마이그레이션 없음).

**확인이 필요한 점 하나**

`package.json`에서는 winston이 빠지고 pino가 들어갔는데, `src/logger.js`는 아직 `require('winston')` 상태입니다. 이대로면 서버가 기동되지 않습니다. ADR의 Risks와 Implementation 체크리스트에 적어뒀습니다. 이 스킬은 `docs/adr/` 안의 파일만 건드리므로 `src/logger.js`는 수정하지 않았습니다 — 제가 pino 기반으로 교체해드릴까요?
