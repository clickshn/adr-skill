ADR-003을 새로 만들었습니다: `docs/adr/ADR-003-pino-logger.md`

기존 ADR이 001, 002까지 있어서 003번을 부여했습니다.

핵심 내용:
- **Status:** Proposed — 새로 내리는 결정이라 package.json이 이미 바뀌어 있어도 Proposed로 시작합니다.
- **Evidence:** autocannon 실측(p99 38ms → 21ms, 8.2k → 11.5k req/s)만 Benchmark에 넣었습니다.
- **Alternatives:** winston 유지(현행)와 bunyan 두 가지. bunyan은 "마지막 릴리스 3년 전"을 기각 사유로, 말씀하신 "유지보수 재개되면 다시 볼 수 있다"를 Recheck if로 적었고 Review Trigger에도 반영했습니다.
- **Risks:** package.json에서는 winston이 빠졌는데 `src/logger.js`는 아직 `winston.createLogger`를 쓰고 있습니다. 이 상태로 배포하면 모듈 해석이 깨지니 코드 교체가 먼저입니다. Implementation 체크리스트 첫 항목으로 넣어뒀습니다.
- **Reversibility:** Yes / Migration Cost Low. 롤백 기준점은 현재 HEAD(6abee39, winston 상태)입니다.

Decision Source는 Human이라 Confidence 필드는 생략했고, PR/이슈 참조가 없어 References 섹션도 만들지 않았습니다. 수정한 파일은 `docs/adr/` 안의 새 파일 하나뿐이며 `src/logger.js`나 package.json은 건드리지 않았습니다.
