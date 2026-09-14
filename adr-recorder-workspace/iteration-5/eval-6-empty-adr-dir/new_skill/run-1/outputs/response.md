ADR을 작성했어요: `docs/adr/001-switch-api-auth-to-jwt.md`

`docs/adr/`에 `.gitkeep`만 있고 기존 ADR이 없어서 **001번부터** 시작했습니다.

**담은 내용**
- **결정:** partner-gateway API 인증을 express-session 쿠키 세션에서 jsonwebtoken(^9.0.2) 기반 JWT로 전환 (Decision Source: Human)
- **배경:** 파트너사 서버가 붙으면서 서버 간 호출에서 쿠키를 다루기가 번거로워짐
- **기각한 대안:** 세션을 유지하면서 파트너용 API 키 발급. 키 회전 관리를 따로 만들어야 해서 접은 것으로 적었고, 키 발급과 회전을 대신 처리할 수단(시크릿 관리 도구, API 게이트웨이 등)이 생기면 다시 검토하도록 Review Trigger에 넣었어요.
- **되돌리기:** 지금은 `package.json`만 바뀌어서 `git checkout HEAD -- package.json`이면 되돌릴 수 있습니다. 파트너가 JWT로 연동한 뒤에는 파트너 쪽 코드도 되돌려야 해서 Partial로 적었어요.
- 벤치마크 같은 실측 수치가 없어서 Evidence 섹션은 넣지 않았습니다.

**확인해 주세요: `src/auth.js`가 아직 세션 방식이에요**
`package.json`에서 express-session은 빠졌는데, `src/auth.js`는 여전히 `require('express-session')`을 호출합니다. 이대로 의존성을 새로 설치하고 배포하면 `Cannot find module 'express-session'` 오류로 서버가 뜨지 않아요. Risks와 Implementation 체크리스트에 적어 두었고, `src/auth.js`는 제가 고치지 않았습니다.

Status는 **Proposed**로 두었어요. `src/auth.js`까지 JWT로 바꾸고 나면 Accepted로 올리면 됩니다.
