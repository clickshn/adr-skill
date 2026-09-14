ADR을 `docs/adr/ADR-003-pino-logger.md`로 작성했어요. 상태는 새 결정이라 Proposed로 뒀어요.

- **Evidence:** autocannon 결과를 넣었어요. p99가 38ms에서 21ms로 약 45% 줄었고, 처리량은 8.2k에서 11.5k req/s로 약 40% 늘었어요.
- **Alternatives:** winston을 그대로 쓰는 안은 벤치마크 결과 때문에 뺐다고 적었어요. bunyan은 마지막 릴리스가 3년 전이라 뺐다고 적었고요.
- **Review Trigger:** bunyan 유지보수가 다시 시작되면 재검토한다고 넣었어요.

**지금 상태로는 서버가 안 뜰 거예요.** `package.json`에서 winston은 뺐는데 `src/logger.js`가 아직 `require('winston')`을 쓰고 있어요. 그래서 새로 `npm install`한 환경에서는 `Cannot find module 'winston'` 에러가 나요. ADR의 Risks와 Implementation에도 적어 뒀어요.

로그 형식도 바뀌어요. pino는 메시지 키가 `message`가 아니라 `msg`이고, level을 숫자(info는 30)로 찍어요. 로그 수집 쪽 쿼리나 대시보드가 winston 형식에 맞춰져 있으면 손봐야 해요.

벤치마크 조건(동시 연결 수, 지속 시간, 대상 엔드포인트)을 알려주시면 Evidence에 추가할게요.

`src/logger.js`도 `pino({ level: 'info' })`로 바꿔드릴까요? 로거를 쓰는 곳은 `server.js` 한 곳뿐이고 문자열만 넘기고 있어서, 그쪽은 고칠 필요가 없어요.
