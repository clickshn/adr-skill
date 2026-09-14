`docs/adr/ADR-003-pino-logger.md`를 만들었습니다. `docs/adr/`에 ADR-001, ADR-002가 있어서 다음 번호인 003을 붙였습니다.

**기록한 내용**
- **Status:** Proposed. 새로 내리는 결정이라 package.json이 이미 바뀌었어도 Proposed로 시작합니다.
- **Evidence:** autocannon 결과, p99 38ms → 21ms(약 45% 감소), 처리량 8.2k → 11.5k req/s(약 40% 증가)
- **Alternatives:** winston 유지(현행), bunyan(마지막 릴리스 3년 전이라 기각)
- **Review Trigger:** bunyan 유지보수가 재개되면 다시 검토
- **Reversibility:** Yes / Low. 변경이 아직 커밋되지 않았으니 `git checkout HEAD -- package.json`으로 되돌릴 수 있습니다.

**확인하셔야 할 점**
1. **`src/logger.js`가 아직 `require('winston')`입니다.** 지금 package.json으로 새로 설치하면 winston이 없어서 서버가 뜨지 않습니다(`Cannot find module 'winston'`). ADR의 Risks와 Implementation에 미완료 항목으로 적어 뒀습니다. 이 스킬은 `docs/adr/` 밖의 파일을 확인 없이 고치지 않아서 logger.js는 그대로 두었습니다. 원하시면 pino로 바꿔 드리겠습니다.
2. **로그 JSON 형식이 바뀝니다.** winston의 `{"level":"info","message":...}`가 pino에서는 `{"level":30,...,"msg":...}`가 됩니다. 로그를 파싱하는 수집이나 알림 설정이 있다면 함께 고쳐야 합니다. Consequences의 Negative에 적었습니다.
3. 벤치마크 측정 조건(연결 수, 지속 시간, 엔드포인트)을 몰라서 Evidence에 "조건 미기록"이라고 적었습니다. 알려주시면 채우겠습니다.
