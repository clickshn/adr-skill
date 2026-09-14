ADR을 남겼습니다: `docs/adr/ADR-003-pino-logger.md`

- **번호:** docs/adr/에 ADR-001, ADR-002가 이미 있어서 003을 붙였습니다.
- **Status:** Proposed. package.json은 이미 바뀌었지만 새로 내리는 결정이라 Proposed로 시작했습니다.
- **Decision Source:** Human. 사용자가 직접 내린 결정이라 Confidence 필드는 넣지 않았습니다.
- **Evidence:** autocannon 결과를 넣었습니다. p99는 38ms → 21ms, 처리량은 8.2k → 11.5k req/s입니다.
- **Alternatives:**
  - winston 유지(현행): 벤치마크에서 불리해 기각.
  - bunyan: 마지막 릴리스가 3년 전이라 기각. "유지보수 재개 시 재검토"를 Recheck if와 Review Trigger에 넣었습니다.

**확인이 필요한 부분이 하나 있습니다.** package.json에서는 winston이 빠졌는데 `src/logger.js`는 아직 `require('winston')`을 씁니다. 이대로 새로 설치하면 서버를 시작할 때 `Cannot find module 'winston'` 오류가 납니다. 이 내용을 ADR의 Risks와 Implementation 체크리스트(미완료 항목)에 적어 두었습니다. 옮길 호출부는 `src/server.js`의 `logger.info` 1곳뿐입니다.

이 스킬은 docs/adr/ 안의 파일만 건드려서 `src/logger.js`는 수정하지 않았습니다. pino로 옮기는 작업이 필요하면 말씀해 주세요.
