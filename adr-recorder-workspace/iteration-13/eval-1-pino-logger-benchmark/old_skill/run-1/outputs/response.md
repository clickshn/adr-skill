`docs/adr/ADR-003-pino-logger.md`로 ADR을 기록했습니다.

기존 ADR이 001, 002까지 있어서 다음 번호인 003으로 붙였습니다.

주요 내용:

- **Status:** Proposed — 새로 내린 결정이라 코드/의존성이 이미 바뀌어 있어도 Proposed로 시작합니다.
- **Decision Source:** Human (직접 결정하신 내용이라 Confidence 필드는 생략)
- **Evidence:** autocannon 측정치 그대로 — p99 38ms → 21ms, 처리량 8.2k → 11.5k req/s
- **Alternatives:** winston 유지(현행)와 bunyan 두 가지. bunyan은 "마지막 릴리스 3년 전"을 기각 사유로, 말씀하신 "유지보수 재개되면 재검토"를 Recheck if로 넣었고 Review Trigger에도 그대로 반영했습니다.
- **Reversibility:** Yes / Migration Cost Low, 복원 기준점은 현재 HEAD인 a20723d로 적었습니다.

한 가지 확인하실 점이 있습니다. `package.json`에서는 winston이 빠지고 pino가 들어갔는데, `src/logger.js`는 아직 `require('winston')` 상태입니다. 이대로면 서버가 기동되지 않아서 ADR의 Risks와 Implementation 체크리스트에 항목으로 남겨뒀습니다. 이 스킬은 `docs/adr/` 밖의 파일은 건드리지 않으니 `src/logger.js` 교체가 필요하면 따로 말씀해 주세요.
