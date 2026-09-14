ADR을 `docs/adr/ADR-003-pino-logger.md`에 남겼어요. 기존 ADR이 001, 002까지 있어서 003을 붙였습니다.

**ADR에 적은 내용**
- **Evidence:** autocannon 결과로 p99 38ms → 21ms, 처리량 8.2k → 11.5k req/s를 넣었어요. autocannon 옵션(연결 수, 지속 시간)은 받은 적이 없어서 미기록이라고 표시했습니다.
- **Alternatives:** bunyan은 "마지막 릴리스가 3년 전"이라는 사유로 기각했고, "유지보수 재개 시 재검토"를 Review Trigger에 넣었어요. 벤치마크에서 밀린 "winston 유지"도 대안으로 같이 적었습니다.
- **Status:** 템플릿 기본값인 `Proposed`로 두었어요. 확정된 결정이면 `Accepted`로 바꾸시면 됩니다.

**확인이 필요한 부분**
- `src/logger.js`에 아직 `require('winston')`이 남아 있어요. 그런데 package.json에서는 winston이 빠져서, 새로 `npm install`하면 서버가 뜨지 않을 거예요. ADR의 Risks와 Implementation에 적어두었고, 코드 파일은 건드리지 않았습니다.
- pino는 로그 레벨을 숫자(info=30)로 출력해요. 로그 수집이나 알림 규칙이 winston의 문자열 `"level":"info"`를 기준으로 되어 있다면 같이 확인해 보세요.

`src/logger.js`를 pino로 바꾸는 작업도 해드릴까요?
