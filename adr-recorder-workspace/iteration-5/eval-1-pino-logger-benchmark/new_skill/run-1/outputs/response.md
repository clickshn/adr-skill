`docs/adr/ADR-003-pino-logger.md`에 winston → pino 교체 결정을 ADR로 남겼습니다. 기존 ADR이 001·002까지 있어서 번호는 003입니다.

**정리한 내용**
- **Status:** Accepted. 결정이 이미 내려졌고 package.json에도 반영돼 있어서 이렇게 뒀습니다. 아직 검토 단계라면 Proposed로 바꿔 주세요.
- **Decision Source:** Human이라서 Confidence 필드는 뺐습니다.
- **Evidence:** 알려주신 autocannon 결과를 넣었습니다(p99 38→21ms, 초당 8.2k→11.5k req). 측정 조건(connections, duration 등)은 대화에 없어서 "기록되지 않음"으로 적었습니다.
- **Alternatives:** bunyan은 마지막 릴리스가 3년 전이라 기각했다고 적었습니다. winston 유지(현상 유지)도 벤치마크 차이를 근거로 기각한 대안으로 넣었습니다.
- **Review Trigger:** "bunyan 유지보수가 재개되는 경우"를 넣었습니다.
- **Reversibility:** Yes / Low. 로거 사용처가 `src/logger.js` 한 곳에 모여 있어서 package.json과 이 파일만 되돌리면 됩니다.

**확인이 필요한 점**
1. `package.json`은 pino로 바뀌었지만 `src/logger.js`는 아직 `require('winston')` 그대로입니다. 이 상태로 의존성을 다시 설치하면 서버 기동 때 `Cannot find module 'winston'` 에러가 납니다. ADR의 Risks와 Implementation 체크리스트에 적어 두었습니다.
2. pino는 기본적으로 `level`을 숫자(`30`)로 찍고, winston은 `"info"` 같은 문자열로 찍습니다. 로그 수집·알림이 문자열 level에 의존한다면 설정을 맞춰야 합니다. 이것도 Risks에 넣었습니다.

이번 작업에서는 `docs/adr/` 밖의 파일은 건드리지 않았습니다. `src/logger.js`를 pino로 바꾸는 것도 진행할까요?
