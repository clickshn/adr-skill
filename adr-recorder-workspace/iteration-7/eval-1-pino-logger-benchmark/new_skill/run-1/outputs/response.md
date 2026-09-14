ADR을 작성했습니다: `docs/adr/ADR-003-winston-to-pino-logger.md`

기존 ADR이 001, 002까지 있어서 이번 결정은 003번입니다.

**내용 요약**
- **Status:** Proposed. package.json은 이미 바뀌었지만 새로 내린 결정이라 Proposed로 시작합니다. 확정되면 Accepted로 바꿔 주세요.
- **Decision Source:** Human. 사람이 내린 결정이라 Confidence 필드는 넣지 않았습니다.
- **Evidence:** autocannon 측정 결과를 적었습니다. p99는 38ms → 21ms, 처리량은 초당 8.2k → 11.5k req입니다. 측정 조건(동시 연결 수, 지속 시간, 대상 엔드포인트)은 받지 못해서 "기록되지 않음"으로 표시했습니다.
- **Alternatives:**
  - winston 유지(현행): 벤치마크 결과가 더 나빠서 기각했습니다.
  - bunyan: 마지막 릴리스가 3년 전이라 제외했습니다. "유지보수가 재개되면 재검토"를 Recheck if와 Review Trigger에 넣었습니다.
- **Reversibility:** Yes / Low. 로거를 `src/logger.js` 한 곳에서만 만들어 쓰고 있어서 되돌리기 쉽습니다.

**확인이 필요한 점(Risks에 기록함)**
- **서버가 시작되지 않을 수 있습니다.** package.json에서는 winston이 빠졌지만 `src/logger.js`는 아직 `require('winston')`을 호출합니다. 이 상태로 새로 설치하면 서버가 `Cannot find module 'winston'` 오류로 뜨지 않습니다. 이 스킬은 docs/adr/ 밖의 파일을 고치지 않기 때문에 `src/logger.js`는 그대로 두었고, Implementation 체크리스트의 미완료 항목으로 남겼습니다. 원하시면 pino 버전으로 바꿔 드리겠습니다.
- **로그 형식이 달라집니다.** pino 기본 출력은 `level`이 숫자이고 메시지 키가 `msg`입니다. 로그 수집, 검색, 알림이 winston 형식(`level: "info"`, `message`)에 맞춰져 있다면 필드 매핑을 조정해야 합니다.
