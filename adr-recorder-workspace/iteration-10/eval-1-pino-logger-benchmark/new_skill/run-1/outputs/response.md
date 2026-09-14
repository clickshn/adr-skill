`docs/adr/ADR-003-pino-logger.md`에 ADR을 새로 만들었습니다. 기존 ADR이 001, 002까지 있어서 번호는 003입니다.

**요약**
- **Status:** Proposed (새로 내린 결정이라 코드가 이미 바뀌었어도 Proposed로 시작합니다)
- **Decision:** order-api 로거를 winston에서 pino로 교체 (pino ^9.4.0, 개발용 pino-pretty ^11.2.2)
- **Evidence:** autocannon 측정 결과 p99 38ms → 21ms, 처리량 초당 8.2k → 11.5k req
- **Alternatives:** winston 유지(성능이 낮아 기각), bunyan(마지막 릴리스가 3년 전이라 기각)
- **Review Trigger:** bunyan 유지보수가 재개되면 다시 검토
- **Reversibility:** Yes / Low. package.json과 src/logger.js만 되돌리면 됩니다.

**확인이 필요한 문제**
- `src/logger.js`가 아직 `require('winston')`을 쓰고 있습니다. package.json에서 winston을 뺐기 때문에 새로 설치하면 서버 시작 시 `Cannot find module 'winston'` 오류가 납니다. ADR의 Risks와 Implementation에 적어 두었습니다. 이 스킬은 docs/adr/ 밖의 파일을 고치지 않아서 logger.js는 그대로 두었습니다.
- 벤치마크 측정 조건(엔드포인트, 동시 연결 수, 측정 시간)을 말씀해 주시지 않아서 기록되지 않았다고 적었습니다. 다시 측정할 때 조건도 함께 남기시면 좋습니다.
