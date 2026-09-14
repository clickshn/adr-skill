`docs/adr/ADR-003-pino-logger.md`에 ADR 남겼어요. 기존 ADR이 001, 002까지 있어서 003으로 이어 붙였습니다.

**담은 내용**
- **Status:** Proposed. 새로 내린 결정이라 이렇게 뒀어요. 적용하고 나면 Accepted로 바꾸시면 됩니다.
- **Decision Source:** Human
- **Evidence:** autocannon 결과를 적었어요. winston p99 38ms / 8.2k req/s → pino p99 21ms / 11.5k req/s로, 지연은 약 45% 줄고 처리량은 약 40% 늘었습니다.
- **Alternatives:**
  - winston 유지: 벤치마크에서 밀려서 기각
  - bunyan: 마지막 릴리스가 3년 전이라 기각. Recheck if에 "유지보수 재개"를 적었고, 이 조건을 Review Trigger에도 넣었어요.
- **Reversibility:** Yes / Low. 로거 생성부(`src/logger.js`) 한 곳과 호출부(`src/server.js`) 한 곳만 바꾸면 돼서 되돌리기 쉬워요.

**확인이 필요한 점**
- **서버가 뜨지 않을 상태예요.** `package.json`에서는 winston을 뺐는데 `src/logger.js`는 아직 `require('winston')`을 쓰고 있어요. 이대로 새로 설치하면 서버 시작할 때 `MODULE_NOT_FOUND`로 실패합니다. ADR의 Risks와 Implementation 체크리스트에 적어뒀어요. 원하시면 `src/logger.js`도 pino로 바꿔드릴게요.
- **pino-pretty는 운영 환경에서 쓰면 안 돼요.** devDependency로 들어가 있어서 운영 설치에는 빠집니다. 운영에서 pretty 출력을 켜면 모듈을 못 찾아요. 개발 환경에서만 쓰도록 분기하는 항목을 체크리스트에 넣었습니다.
- **벤치마크 조건이 빠져 있어요.** 연결 수, 측정 시간, 대상 엔드포인트를 알려주시면 Evidence에 추가할게요. 나중에 bunyan을 다시 비교할 때 같은 조건으로 돌리려면 필요합니다.
