ADR을 작성했습니다: `docs/adr/001-api-auth-session-to-jwt.md`

`docs/adr/`에는 `.gitkeep`만 있고 기존 ADR이 없어서 **ADR-001**로 시작했습니다.

**요약**
- **결정:** partner-gateway의 API 인증을 express-session 쿠키 세션에서 jsonwebtoken 기반 JWT로 교체
- **배경:** 파트너 주문 조회 API(abe4c7c) 이후 파트너사 서버가 붙으면서 쿠키 기반 인증이 번거로워짐
- **기각한 대안:** 세션 유지 + 파트너용 API 키 발급. 키 회전 관리를 따로 만들어야 해서 접은 것으로 기록했고, Review Trigger는 "키 발급·회전 관리를 별도 구현 없이 제공받게 되는 경우"로 적었습니다.
- **Decision Source:** Human (그래서 Confidence는 넣지 않았습니다). 실측 수치가 없어 Evidence 섹션도 넣지 않았습니다.
- **Status:** 템플릿 기본값인 Proposed로 두었습니다. 팀 합의가 끝났으면 Accepted로 바꾸시면 됩니다.

**확인이 필요한 점**
`package.json`에서는 express-session을 뺐는데 `src/auth.js`는 아직 `require('express-session')`로 세션 미들웨어를 쓰고 있습니다. 이대로 의존성을 새로 설치하고 실행하면 모듈을 찾지 못해 서버가 뜨지 않습니다. 이 내용은 ADR의 Risks와 Implementation 체크리스트에 적어 두었고, `src/auth.js`는 수정하지 않았습니다. JWT 검증 미들웨어로 바꾸는 작업도 할까요?
