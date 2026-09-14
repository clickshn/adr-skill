`docs/adr/ADR-003-pino-logger.md`를 만들었습니다. ADR-001, ADR-002가 이미 있어서 번호는 003으로 이어 붙였습니다.

**기록한 내용**
- **Status:** Proposed. 새로 내린 결정이라 package.json이 이미 바뀌었어도 Proposed로 시작합니다.
- **Decision Source:** Human이라 Confidence 필드는 뺐습니다.
- **Evidence:** autocannon 측정 결과를 적었습니다. p99는 38ms → 21ms, 처리량은 8.2k → 11.5k req/s입니다.
- **Alternatives:**
  - winston 유지(현행): 벤치마크에서 열세라 기각했습니다.
  - bunyan: 마지막 릴리스가 3년 전이라 기각했습니다. 말씀하신 "유지보수가 재개되면 다시 검토"는 Recheck if와 Review Trigger에 넣었습니다.
- **Reversibility:** Yes, 비용 Low. winston 구성이 들어 있는 커밋은 f057b95입니다(`git show --stat`으로 확인). 이 커밋에서 `package.json`과 `src/logger.js`를 복원하면 되돌릴 수 있습니다.

**확인이 필요한 점**
- `src/logger.js`가 아직 `require('winston')`을 쓰고 있습니다. package.json에서는 winston이 빠졌기 때문에, 의존성을 새로 설치하면 서버가 뜨지 않습니다. 이 내용은 ADR의 Risks와 Implementation 체크리스트에 적어 두었습니다. 이 스킬은 `docs/adr/` 밖의 파일은 수정하지 않아서 코드는 그대로 두었습니다. 원하시면 logger.js 전환도 진행하겠습니다.
- pino로 바꾸면 로그 필드 형식이 달라집니다. `level`이 문자열에서 숫자로, `message`가 `msg`로 바뀝니다. 로그 수집이나 알림이 이 필드명에 의존하고 있다면 점검이 필요하고, 이것도 Risks에 적었습니다.
- 벤치마크 측정 조건(연결 수, 지속 시간, 엔드포인트)은 기록이 없어서 Evidence에 "기록되지 않음"으로 표시했습니다. 알려주시면 보강하겠습니다.
