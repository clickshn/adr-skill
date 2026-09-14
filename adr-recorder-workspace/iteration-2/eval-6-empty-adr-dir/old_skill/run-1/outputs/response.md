ADR을 `docs/adr/001-api-auth-session-to-jwt.md`로 작성했습니다. `docs/adr/`에는 `.gitkeep`만 있어서 첫 번호인 ADR-001을 붙였습니다.

**담은 내용**
- **결정:** partner-gateway API 인증을 express-session 쿠키 세션에서 jsonwebtoken 기반 JWT로 전환합니다. 새 결정이라 Status는 Proposed로 뒀습니다.
- **배경:** 파트너사 서버가 API에 붙으면서 쿠키 기반 인증이 번거로워졌다는 점을 적었습니다.
- **대안:** "세션 유지 + 파트너용 API 키 발급"을 넣었고, 기각 사유는 키 회전 관리를 따로 만들어야 한다는 점입니다. 이 대안의 재검토 조건이 Review Trigger 항목으로 들어갔습니다.
- **Evidence:** 실측 수치가 없어서 이 섹션은 만들지 않았습니다. Decision Source가 Human이라 Confidence도 적지 않았습니다.

**확인이 필요한 점**
- `package.json`에서는 express-session을 뺐지만 `src/auth.js`는 아직 `require('express-session')`로 세션 미들웨어를 내보내고 있습니다. 이대로 클린 설치하면 서버가 뜨지 않습니다. 이 내용은 ADR의 Risks와 Implementation에 적어 뒀습니다.
- JWT도 서명 키를 회전해야 하므로, API 키 안을 기각한 이유와 같은 종류의 운영 부담이 조금 남습니다. 이 내용은 Risks에 한 줄로 적었습니다.

이 결정에서 기각한 대안과 수치적 근거를 알려주세요. 예를 들어 파트너사 수, 키 회전 주기, 키 관리 기능을 만드는 데 드는 예상 공수 같은 것들입니다. 알려주시면 Alternatives와 Evidence에 반영하겠습니다.
