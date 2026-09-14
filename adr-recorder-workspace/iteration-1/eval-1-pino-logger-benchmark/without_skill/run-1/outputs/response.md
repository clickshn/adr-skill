ADR을 `docs/adr/ADR-003-pino-logger.md`에 남겼어요. 형식은 기존 ADR-001, 002와 같아요. 커밋은 아직 안 했어요.

**ADR에 넣은 내용**
- **결정:** order-api 로거를 winston 3에서 pino `^9.4.0`으로 바꾸고, 로컬 개발용으로 pino-pretty `^11.2.2`를 devDependency로 둠
- **근거:** autocannon으로 잰 결과를 표로 넣었어요.
  - p99 지연: 38ms에서 21ms로 약 45% 줄었어요.
  - 처리량: 초당 8.2k에서 11.5k req로 약 40% 늘었어요.
- **대안:**
  - winston 유지: 성능이 밀려서 뺐어요.
  - bunyan: 마지막 릴리스가 3년 전이라 뺐어요.
- **다시 볼 조건:** bunyan 유지보수가 재개되면 다시 검토

**확인할 것**
1. **지금 서버가 안 뜰 거예요.** `src/logger.js`가 아직 `require('winston')`을 쓰는데, package.json에서 winston이 빠졌어요. 이 파일을 pino로 옮겨야 하고, ADR의 후속 작업에도 적어 뒀어요. 원하면 바로 고칠게요.
2. **측정 조건을 알려주세요.** 동시 연결 수, 측정 시간, 대상 엔드포인트, 로그 레벨을 몰라서 ADR에는 "기록되지 않음"으로 적었어요. 알려주면 채워 넣을게요.
3. **로그 형식이 달라져요.** pino는 `level`을 숫자로 찍고 `time`, `pid`, `hostname` 필드를 붙여요. 로그 수집, 검색, 알림 규칙이 winston 형식에 맞춰져 있다면 같이 봐야 해요. 이것도 ADR의 Consequences에 적어 뒀어요.
