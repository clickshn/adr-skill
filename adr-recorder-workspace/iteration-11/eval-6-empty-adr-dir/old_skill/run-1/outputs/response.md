ADR을 작성했습니다.

**생성:** `docs/adr/001-api-auth-session-to-jwt.md` — ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- `docs/adr/`에는 `.gitkeep`만 있고 기존 ADR이 없어서 **001번부터 시작**했습니다.
- **Status: Proposed** — 코드(`package.json`)가 이미 바뀌어 있어도 새로 내린 결정이라 Proposed로 뒀습니다. 확정되면 Accepted로 바꿔 주세요.
- **Decision Source: Human** — 말씀하신 결정을 그대로 기록했으므로 Confidence는 생략했습니다.
- **Alternatives** — 대화에 나온 두 가지만 정리했습니다.
  - 현행 유지(express-session 쿠키 세션): 파트너사 서버가 붙으면서 쿠키 기반이 번거로워져 기각
  - 세션 유지 + 파트너용 API 키 발급: 키 회전 관리를 따로 만들어야 해서 기각
- 재검토 조건은 말씀하신 게 없어서 Recheck if와 Review Trigger는 넣지 않았습니다. 측정 수치가 없으니 Evidence 섹션도 뺐습니다.
- Reversibility는 저장소에서 확인한 대로 적었습니다. 지금은 `package.json`만 바뀐 상태라 `git checkout HEAD -- package.json`으로 되돌릴 수 있습니다(Migration Cost: Low).

**확인이 필요한 점:** `src/auth.js`가 아직 `require('express-session')`을 호출합니다. 의존성을 뺀 상태로 설치하고 서버를 띄우면 모듈을 찾지 못해 시작되지 않습니다. ADR의 Risks와 Implementation 체크리스트에 적어 두었습니다. 이 스킬은 `docs/adr/` 밖의 파일은 수정하지 않기 때문에 `src/auth.js`는 건드리지 않았습니다.
