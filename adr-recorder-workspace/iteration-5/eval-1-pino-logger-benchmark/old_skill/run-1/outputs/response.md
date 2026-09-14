ADR을 `docs/adr/ADR-003-pino-logger.md`로 만들었어요. 기존 ADR이 001, 002라서 003번을 붙였고, 기존 파일명 규칙(`ADR-NNN-slug.md`)을 따랐습니다.

**들어간 내용**
- **결정:** order-api 로거를 winston 3에서 pino 9로 교체(dev에는 pino-pretty). 사용자 결정이라 Status는 Accepted, Decision Source는 Human으로 두고 Confidence는 생략했어요.
- **Evidence:** autocannon 결과를 넣었어요. p99 38ms → 21ms(약 45% 감소), 처리량 8.2k → 11.5k req/s(약 40% 증가).
- **Alternatives:**
  - bunyan: 마지막 릴리스가 3년 전이라 기각. Recheck if는 "유지보수 재개 시"로 적었고, 이게 Review Trigger에도 들어가요.
  - winston 유지: 벤치마크에서 밀려서 기각.
- **Reversibility:** 롤백 쉬움(Low). 호출부가 `src/server.js` 1곳뿐이라 winston ^3.13.0과 이전 logger.js로 되돌리기만 하면 됩니다.

**확인이 필요한 부분**
1. **`src/logger.js`가 아직 `require('winston')`을 쓰고 있어요.** package.json에서는 winston이 빠졌기 때문에, 이대로 `npm install` 후 배포하면 서버가 기동할 때 `Cannot find module 'winston'`으로 죽습니다. ADR의 Risks와 Implementation 체크리스트에 적어 두었어요. 이 스킬은 `docs/adr/` 밖의 파일을 직접 고치지 않아서 코드는 건드리지 않았습니다.
2. **로그 포맷이 바뀝니다.**
   - winston은 `level:"info"`, `message`로 남기고, pino는 `level:30`, `msg`, `time`, `pid`, `hostname`으로 남깁니다.
   - 로그 수집·알림 규칙이 winston 필드에 의존하고 있다면 같이 손봐야 해요. 이것도 Consequences에 적어 두었습니다.
3. **벤치마크 측정 조건이 빠져 있어요.** 연결 수, 지속 시간, 대상 엔드포인트를 알려주시면 Evidence에 추가하겠습니다. 없어도 ADR로서는 문제없어요.

`src/logger.js`를 pino로 바꾸는 작업도 이어서 할까요?
