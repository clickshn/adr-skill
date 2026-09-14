`docs/adr/ADR-003-pino-logger.md`를 만들었습니다. 기존 ADR이 001(Express), 002(PostgreSQL)까지 있어서 003을 붙였습니다.

**기록한 내용**
- **Status:** Proposed. package.json은 이미 바뀌었지만 새로 내리는 결정이라 Proposed로 시작합니다.
- **Decision Source:** Human. 직접 내린 결정이라 Confidence는 넣지 않았습니다.
- **Evidence:** autocannon 결과입니다. p99는 38ms에서 21ms로 약 45% 줄었고, 처리량은 8.2k에서 11.5k req/s로 약 40% 늘었습니다.
- **Alternatives:**
  - winston 유지: 벤치마크 수치 때문에 기각했습니다.
  - bunyan: 마지막 릴리스가 3년 전이라 기각했습니다. "유지보수 재개 시 재검토"는 Recheck if와 Review Trigger에 넣었습니다.
- **Reversibility:** Yes / Low. 로거 사용처가 `src/logger.js` 한 곳뿐이라 package.json과 이 파일만 되돌리면 됩니다.

**확인이 필요한 점** (ADR의 Risks와 Implementation에도 적었습니다)
1. **`src/logger.js`가 아직 `require('winston')` 상태입니다.** package.json에서 winston이 빠졌기 때문에, 새로 `npm install`/`npm ci`를 하면 서버가 시작할 때 `Cannot find module 'winston'`으로 실패합니다. 이 파일은 docs/adr/ 밖이라 수정하지 않았습니다.
2. **로그 스키마가 바뀝니다.** winston의 `message`와 문자열 `level`이 pino에서는 `msg`와 숫자 `level`(info=30)로 나옵니다. 로그 수집·알림 규칙이 이 필드들을 쓰는지 확인해 주세요.
3. **벤치마크 측정 조건이 없습니다.** 대상 엔드포인트, 동시 연결 수, 지속 시간이 없어 Evidence에 "조건 미기록"으로 적어 두었습니다. 알려주시면 추가하겠습니다.
