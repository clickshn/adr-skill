`docs/adr/ADR-003-pino-logger.md`를 만들었어요. 기존 ADR이 001(Express)과 002(PostgreSQL)까지 있어서 003을 붙였어요.

**ADR에 담은 내용**
- **Status:** Proposed. 새로 내린 결정이라 이렇게 뒀어요. Decision Source는 Human이에요.
- **Evidence:** autocannon 결과를 넣었어요. p99는 38ms에서 21ms로 약 45% 줄었고, 처리량은 8.2k에서 11.5k req/s로 약 40% 늘었어요. 측정 조건(동시 연결 수, 측정 시간)은 기록된 게 없어서 없다고 한 줄 적었어요.
- **Alternatives:** 두 가지를 적었어요.
  - winston 유지: 벤치마크 수치 때문에 기각했어요.
  - bunyan: 마지막 릴리스가 3년 전이라 기각했어요. "유지보수 재개 시" 다시 보는 조건은 Review Trigger에도 넣었어요.
- **Reversibility:** 되돌리기 쉬워요(Migration Cost Low). 로거를 쓰는 곳이 `src/logger.js`와 `src/server.js` 한 곳뿐이에요.

**확인이 필요한 문제**
- **서버가 안 뜰 수 있어요.** `src/logger.js`가 아직 `require('winston')`을 쓰고 있어요. 그런데 package.json에서는 winston이 빠졌어요. 새로 `npm install`한 환경에서는 `Cannot find module 'winston'` 오류로 서버가 뜨지 않아요. ADR의 Risks와 Implementation 체크리스트에 적어뒀어요.
- **로그 형태가 바뀌어요.** winston은 `level: "info"`, `message`로 찍고 pino는 `level: 30`, `msg`로 찍어요. 로그 수집이나 검색 쿼리가 이 필드를 쓰고 있다면 고쳐야 해요. Consequences의 Negative에 적었어요.

`src/logger.js`를 pino 버전으로 바꿔 드릴까요?
