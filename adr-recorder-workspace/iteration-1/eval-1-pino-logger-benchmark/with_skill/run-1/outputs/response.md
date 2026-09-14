winston에서 pino로 바꾼 결정을 `docs/adr/ADR-003-pino-logger.md`에 ADR로 남겼습니다. 작업 트리의 package.json diff(winston 제거, pino ^9.4.0과 devDependency pino-pretty ^11.2.2 추가)와 말씀해 주신 내용으로 작성했고, 대화에서 나온 결정이라 Status는 **Proposed**로 두었습니다.

- **Evidence:** autocannon 결과입니다. p99는 38ms에서 21ms로 44.7% 줄었고, 처리량은 8.2k에서 11.5k req/s로 40.2% 늘었습니다.
- **Alternatives:**
  - winston(현행 유지): 벤치마크에서 더 느려서 기각했습니다.
  - bunyan: 마지막 릴리스가 3년 전이라 기각했습니다.
- **Review Trigger:** bunyan 유지보수가 재개되면 다시 검토합니다.

**배포 전에 고쳐야 할 문제가 하나 있습니다.** `src/logger.js`는 아직 `require('winston')`을 쓰고 있는데 package.json에서는 winston이 빠졌습니다. 그래서 새로 설치한 환경에서는 서버가 뜨자마자 `MODULE_NOT_FOUND`로 멈춥니다. 이 내용은 ADR의 Risks와 Implementation 체크리스트에 적어 두었습니다.

로거 코드를 옮길 때 하나 더 주의하세요. 메타데이터 인자 순서가 winston은 `info(msg, meta)`이고 pino는 `info(meta, msg)`로 반대입니다. 이것도 Risks에 적어 두었습니다.
