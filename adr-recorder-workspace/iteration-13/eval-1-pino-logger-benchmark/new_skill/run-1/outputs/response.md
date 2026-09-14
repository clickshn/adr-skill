`docs/adr/ADR-003-pino-logger.md`를 만들었습니다.

기존 ADR을 셸로 확인해보니 ADR-001(Express), ADR-002(PostgreSQL)이 있어서 다음 번호인 **003**으로 잡았습니다.

주요 내용은 이렇습니다.

- **Status:** Proposed — 새로 내리는 결정이라 package.json이 이미 바뀌어 있어도 Proposed로 시작합니다.
- **Evidence:** autocannon 측정치를 그대로 기록했습니다 (p99 38ms → 21ms, 처리량 8.2k → 11.5k req/s).
- **Alternatives:** winston 유지(현행)와 bunyan 두 가지를 정리했습니다. bunyan은 "마지막 릴리스 3년 전"을 기각 사유로, 말씀하신 "유지보수 재개 시 재검토"를 Recheck if로 넣었고 이것이 Review Trigger로도 올라갔습니다.
- **Reversibility:** Yes / Migration Cost Low. package.json 변경이 아직 커밋 전이라 `git checkout -- package.json`으로 되돌릴 수 있다는 점, 현재 기준점이 커밋 a20723d라는 점을 적었습니다.

참고로 `src/logger.js`는 아직 winston 기반 그대로입니다(`winston.createLogger`). package.json에서는 winston이 빠졌으니 실제로는 지금 상태로 서버가 뜨지 않습니다. ADR의 Implementation 체크리스트 첫 항목에 넣어뒀는데, 이어서 pino로 교체해드릴까요?
