`docs/adr/ADR-003-pino-logger.md`를 만들었어요. 기존 ADR이 001, 002까지 있어서 003번으로 붙였어요.

**ADR 내용**
- **Status:** Proposed. package.json은 이미 바뀌었지만 새로 내리는 결정이라 Proposed로 시작했어요. 팀에서 확정되면 Accepted로 바꾸면 돼요.
- **Decision Source:** Human이라 Confidence는 생략했어요.
- **Evidence:** 알려주신 autocannon 수치를 그대로 넣었어요. p99는 38ms에서 21ms로(-44.7%), 처리량은 초당 8.2k에서 11.5k req로(+40.2%) 바뀌었어요. 다만 측정 조건(엔드포인트, 동시 연결 수, 측정 시간)은 기록된 게 없어서 그렇다고 적어 두었어요.
- **Alternatives:** bunyan은 "마지막 릴리스 3년 전"이라는 이유로 기각했다고 적었어요. 유지보수가 재개되면 다시 검토하도록 Recheck if와 Review Trigger에 넣었어요.
- **Reversibility:** Yes, 비용은 Low예요. 되돌리려면 package.json을 winston ^3.13.0으로 돌리고 src/logger.js를 HEAD 버전으로 복원하면 돼요.

**확인이 필요한 부분**
`src/logger.js`는 아직 `require('winston')`을 쓰고 있어요. 그런데 package.json에서는 winston이 빠졌어요. 이 상태로 의존성을 새로 설치하면 서버가 시작할 때 `MODULE_NOT_FOUND`로 실패해요. ADR의 Risks와 Implementation 체크리스트에 적어 두었고, 코드는 수정하지 않았어요.

`src/logger.js`를 pino 기반으로 바꿀까요? level `info`와 JSON stdout 출력은 지금처럼 유지할게요.
