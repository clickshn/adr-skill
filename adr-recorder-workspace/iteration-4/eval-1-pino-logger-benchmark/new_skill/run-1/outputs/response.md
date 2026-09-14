`docs/adr/ADR-003-pino-logger.md`에 winston → pino 교체 결정을 ADR로 남겼어요. 기존 ADR이 001, 002까지 있어서 번호는 003으로 이어 붙였어요.

**ADR에 반영한 내용**
- **Evidence:** autocannon 결과를 적었어요. p99는 38ms → 21ms(−17ms, 약 45% 감소), 처리량은 8.2k → 11.5k req/s(+3.3k, 약 40% 증가)예요.
- **Alternatives:**
  - bunyan은 "마지막 릴리스가 3년 전"이라는 기각 사유와 함께 적었어요. "유지보수 재개 시 재검토"는 Review Trigger에 넣었어요.
  - winston을 그대로 쓰는 현행 유지안도 벤치마크 수치를 근거로 기각된 대안으로 넣었어요.
- **Status:** 템플릿 기본값인 `Proposed`로 두었어요. 리뷰가 끝나면 `Accepted`로 바꿔 주세요.

**꼭 확인하셔야 할 점**
1. **`src/logger.js`는 아직 winston을 쓰고 있어요.** package.json에서는 winston이 빠졌는데 `src/logger.js`는 아직 `require('winston')`을 호출해요. 이 상태로 `npm install` 후 서버를 켜면 `Cannot find module 'winston'` 오류로 뜨지 않아요. 이 스킬은 `docs/adr/` 밖의 파일을 고치지 않게 되어 있어서 코드는 손대지 않았고, ADR의 Risks와 Implementation 체크리스트에만 적어 두었어요.
2. **로그 형식이 달라져요.** pino는 기본적으로 `level`을 숫자(30)로, 메시지 키를 `message`가 아니라 `msg`로 출력해요. 로그 수집 쿼리나 알림이 winston 형식에 맞춰져 있다면 필드 매핑을 확인해야 해요. 이 내용은 Negative와 Risks에 적었어요.
3. **벤치마크 측정 조건이 빠져 있어요.** 연결 수, 지속 시간, 실행 환경이 없어서 나중에 다시 재기 어려워요. 알려주시면 Evidence에 추가할게요.

`src/logger.js`도 pino로 바꿔드릴까요?
