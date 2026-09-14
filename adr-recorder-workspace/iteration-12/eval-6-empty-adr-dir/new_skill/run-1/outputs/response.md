ADR을 작성했습니다: `docs/adr/001-jwt-api-authentication.md`

`docs/adr/` 디렉터리에 `.gitkeep`만 있고 기존 ADR 파일이 없어서 **001번으로 시작**했습니다.

기록한 내용:

- **Status:** Proposed — 새로 내리는 결정이라 package.json이 이미 바뀌어 있어도 Proposed로 시작합니다.
- **Context:** 파트너사 서버 연동이 늘면서 브라우저 전제인 쿠키 세션이 서버 대 서버 호출에 맞지 않게 된 상황.
- **Decision:** jsonwebtoken ^9.0.2 추가 / express-session ^1.18.0 제거, 상태 기반 쿠키 인증 → 무상태 토큰 인증.
- **Alternatives:** 세션 유지 + 파트너용 API 키 발급 (키 회전 관리를 따로 만들어야 해서 기각).
- **Consequences / Risks:** 발급된 JWT의 즉시 무효화가 어려운 점, 서명 키 유출 시 영향 범위 확대.
- **Reversibility:** Yes — 세션은 영속 데이터가 아니라 되돌릴 저장소가 없고, 커밋 전이라 HEAD(`2a29f15`) 기준 복원이면 충분합니다.

작성 중 확인한 사항 하나 알려드립니다. **`src/auth.js`가 아직 `require('express-session')`을 그대로 쓰고 있습니다.** package.json에서는 의존성이 빠진 상태라 지금 그대로면 모듈 해석이 실패합니다. ADR의 Risks와 Implementation 체크리스트에 남겨뒀습니다.

대화에 재검토 조건이 언급되지 않아 Recheck if / Review Trigger는 넣지 않았습니다. 나중에 "이런 상황이 되면 API 키 방식을 다시 보겠다" 같은 조건이 정해지면 알려주세요. 추가하겠습니다.
