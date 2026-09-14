ADR-003을 만들었습니다: `docs/adr/ADR-003-pino-logger.md`

- **번호:** docs/adr/에 ADR-001, ADR-002가 있어 다음 번호 003을 붙였습니다.
- **Status:** Proposed. package.json은 이미 바뀌었지만 새로 내리는 결정이라 Proposed로 두었습니다. Accepted로 올리는 건 팀에서 정하시면 됩니다.
- **Evidence:** autocannon 측정값(p99 38ms → 21ms, 처리량 8.2k → 11.5k req/s)을 Benchmark에 적었습니다.
- **Alternatives:** winston 유지(현행)와 bunyan(마지막 릴리스가 3년 전이라 제외)을 정리했습니다. 말씀하신 "bunyan 유지보수가 재개되면 다시 검토"는 bunyan의 Recheck if와 Review Trigger에 넣었습니다.

**확인이 필요한 점:** package.json에서 winston은 빠졌는데 `src/logger.js`는 아직 `require('winston')`을 하고 있습니다. 이 상태로 새로 설치하면 서버가 뜨지 않습니다(`Cannot find module 'winston'`). 이 스킬은 docs/adr/ 밖의 파일은 고치지 않기 때문에 logger.js는 손대지 않았습니다. 대신 ADR의 Implementation에 할 일로, Risks에 위험으로 적어 두었습니다. 원하시면 pino로 전환해 드리겠습니다.

로그 JSON 필드가 바뀌는 점(level이 숫자로 바뀌고 message가 msg로 바뀜)도 로그 수집 쪽에서 확인할 항목으로 Risks에 적었습니다.
