`docs/adr/ADR-003-pino-logger.md`를 만들었어요. 기존에 ADR-001(Express)과 ADR-002(PostgreSQL)가 있어서 다음 번호인 003을 붙였습니다.

**기록한 내용**
- **Status:** Proposed. `package.json`은 이미 바뀌었지만 새로 내리는 결정이라 Proposed로 시작합니다.
- **Evidence:** autocannon 측정 결과. p99 38ms → 21ms(약 44.7% 감소), 처리량 8.2k → 11.5k req/s(약 40.2% 증가).
- **Alternatives:** winston 유지(벤치마크에서 더 느림)와 bunyan(마지막 릴리스가 3년 전).
- **Review Trigger:** bunyan 유지보수가 재개될 때.
- **Reversibility:** Yes, 비용 Low. 로거를 쓰는 곳이 `src/logger.js`와 `src/server.js`의 호출 1곳뿐입니다.

**저장소를 보다가 발견한 문제**
- **`src/logger.js`가 아직 `require('winston')`을 호출해요.** `package.json`에서 winston을 뺐기 때문에, 이 상태로 새로 설치하면 서버 시작 시 모듈을 찾지 못해 실패합니다. 이 스킬은 `docs/adr/` 밖의 파일은 수정하지 않아서 코드는 그대로 뒀어요. ADR의 Implementation 체크리스트와 Risks에 적어 두었습니다.
- pino는 기본 JSON 출력 형태가 winston과 달라요(`level`이 숫자, 메시지 키가 `msg`). 로그 수집·파싱 규칙이 winston 형식에 맞춰져 있다면 함께 고쳐야 합니다. Risks에 적어 두었습니다.
- 벤치마크의 측정 조건(동시 연결 수, 지속 시간, 엔드포인트)은 받지 못해서 "기록되지 않음"으로 남겼어요. 알려주시면 Evidence에 채워 넣겠습니다.
