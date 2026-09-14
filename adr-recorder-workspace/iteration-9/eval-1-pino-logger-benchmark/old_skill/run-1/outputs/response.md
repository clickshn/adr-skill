`docs/adr/ADR-003-pino-logger.md`를 만들었습니다. 기존 ADR이 001, 002까지 있어서 003을 붙였어요.

**요약**
- **Status:** Proposed. package.json은 이미 바뀌었지만 새로 내리는 결정이라 Proposed로 시작했습니다.
- **Decision Source:** Human. 그래서 Confidence는 넣지 않았습니다.
- **Evidence:** autocannon 결과를 적었습니다. p99는 38ms에서 21ms로 약 45% 줄었고, 처리량은 초당 8.2k에서 11.5k req로 약 40% 늘었습니다.
- **Alternatives:** 현행인 winston 유지와 bunyan을 넣었습니다. bunyan은 마지막 릴리스가 3년 전이라 기각했습니다.
- **Review Trigger:** bunyan 유지보수가 재개되면 다시 봅니다.
- **Reversibility:** Yes, 비용 Low. 로거가 `src/logger.js` 한 곳에만 있어서 되돌리기 쉽습니다.

**확인이 필요한 점**
1. **`src/logger.js`가 아직 `require('winston')`을 호출합니다.** package.json에서는 winston이 빠졌기 때문에, 클린 설치 후에는 서버가 기동 단계에서 실패합니다. ADR의 Risks와 Implementation에 적어두었고, 코드는 건드리지 않았습니다(이 스킬은 `docs/adr/` 밖을 수정하지 않습니다). 원하시면 logger.js를 pino로 바꿔드릴게요.
2. pino는 기본 로그 필드가 다릅니다. 숫자 level(`30`), `msg`, `time` 등을 쓰기 때문에, 로그 수집이나 검색 쿼리가 winston 형식(`level: "info"`, `message`)에 맞춰져 있다면 함께 고쳐야 합니다. 이 내용은 Negative에 적었습니다.
3. 벤치마크의 측정 조건(동시 연결 수, 지속 시간, 로그 레벨)이 없어서 Evidence에 "조건 미기록"으로 표시했습니다. 알려주시면 추가할게요.
