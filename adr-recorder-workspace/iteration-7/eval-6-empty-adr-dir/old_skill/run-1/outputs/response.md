ADR을 작성했습니다: `docs/adr/001-api-auth-session-to-jwt.md`

**번호 안내:** `docs/adr/`에는 `.gitkeep`만 있고 기존 ADR이 없어서 ADR-001로 시작했습니다.

**요약**
- **결정:** partner-gateway의 API 인증을 express-session 쿠키 세션에서 jsonwebtoken 기반 JWT로 전환
- **Status:** Proposed (package.json은 이미 바뀌었지만, 새로 내리는 결정이라 Proposed로 시작합니다)
- **Decision Source:** Human
- **Alternatives:** "세션 유지 + 파트너용 API 키 발급" 한 가지를 넣었고, 기각 사유는 말씀하신 대로 "키 회전 관리를 따로 만들어야 함"입니다. Review Trigger에는 "키 회전을 직접 만들지 않아도 되는 수단이 생기면 재검토"를 넣었습니다.
- **Evidence:** 측정 수치가 없어서 섹션을 만들지 않았습니다.
- **Reversibility:** Yes / Migration Cost Medium입니다. 지금은 package.json만 되돌리면 되지만, 파트너가 JWT로 연동한 뒤에는 파트너 쪽도 함께 되돌려야 합니다. 롤백 기준점으로 기존 세션 구성을 도입한 커밋 c398cfc를 References에 적었습니다.

**확인이 필요한 점**
`src/auth.js`가 아직 `require('express-session')`을 그대로 쓰고 있는데 package.json에서는 이 의존성이 빠졌습니다. 이대로 새로 설치해 실행하면 서버가 시작할 때 모듈을 찾지 못해 실패합니다. 그래서 ADR의 Risks와 Implementation 체크리스트에 적어 두었습니다. 스킬 범위상 `docs/adr/` 밖의 파일은 건드리지 않았으니, auth.js를 JWT 검증 미들웨어로 바꾼 뒤에 커밋해 주세요.
