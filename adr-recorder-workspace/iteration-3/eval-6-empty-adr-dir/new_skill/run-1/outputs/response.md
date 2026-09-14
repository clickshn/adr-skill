`docs/adr/001-api-auth-jwt.md`를 작성했어요. `docs/adr/`에는 `.gitkeep`만 있고 기존 ADR이 없어서 001번으로 시작했습니다.

**먼저 확인할 문제:** 지금 작업 트리 상태로는 서버가 뜨지 않아요. package.json에서 `express-session`은 뺐는데 `src/auth.js`는 아직 `require('express-session')`으로 세션 미들웨어를 export하고 있어서, 의존성을 다시 설치하면 `Cannot find module 'express-session'` 오류가 납니다. auth.js를 `jsonwebtoken` 검증 미들웨어로 바꾸는 작업을 package.json 변경과 같은 커밋에 넣는 게 좋겠어요. ADR의 Risks와 Implementation에도 적어 두었습니다.

**ADR 내용**
- **Status:** 새로 내린 결정이라 Proposed로 두었어요. 결정을 사용자가 직접 내렸기 때문에(Decision Source: Human) Confidence 필드는 뺐습니다.
- **배경:** 파트너사 서버가 API를 호출하기 시작했는데, 서버 간 연동에서는 쿠키 세션 방식이 번거롭습니다.
- **기각한 대안:** "express-session 유지 + 파트너용 API 키 발급". 키 회전 관리를 따로 만들어야 해서 접었다고 말씀하신 대로 적었어요. 다시 검토할 조건은 두 가지로 잡았습니다.
  - 키 발급·회전을 대신 처리해 주는 인프라(API 게이트웨이, 시크릿 매니저 등)를 도입할 때
  - 토큰 즉시 폐기 요구가 커져서 어차피 서버 쪽 상태 관리가 필요해질 때
- **Consequences:** 발급한 토큰을 만료 전에 무효화하기 어렵다는 점과 서명 비밀값 관리가 필요하다는 점을 적었어요. JWT 서명 키도 결국 교체 절차가 필요합니다.
- **되돌리기:** 지금은 미커밋 상태인 package.json 한 줄만 되돌리면 됩니다. 파트너가 JWT 방식으로 연동한 뒤에는 파트너 쪽 인증 처리도 함께 되돌려야 해서 Partial로 적었어요.
- **Evidence:** 실측 수치가 없어서 섹션을 만들지 않았습니다.
