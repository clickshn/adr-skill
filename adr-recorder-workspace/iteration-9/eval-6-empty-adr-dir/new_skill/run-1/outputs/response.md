ADR을 작성했습니다: `docs/adr/001-api-auth-jwt.md`

- `docs/adr/`에 기존 ADR이 없고 `.gitkeep`만 있어서 **001번부터 시작**했습니다.
- **Status: Proposed**로 두었습니다. `package.json`은 이미 바뀌었지만 새로 내린 결정이라 제안 상태에서 시작합니다.
- **Decision Source: Human.** 직접 내린 결정이라 Confidence 필드는 뺐습니다. 측정 수치가 없어서 Evidence 섹션도 넣지 않았습니다.
- **Alternatives**에는 말씀하신 두 가지만 정리했습니다.
  - 현행 유지(express-session 쿠키 세션): 파트너사 서버 연동에 쿠키 기반이 번거로워서 기각
  - 세션 유지 + 파트너용 API 키 발급: 키 회전 관리를 따로 만들어야 해서 기각
- 재검토 조건(Recheck if)은 말씀하신 게 없어서 적지 않았고, 그래서 Review Trigger 섹션도 만들지 않았습니다.

**확인이 필요한 점:** `src/auth.js`가 아직 `require('express-session')`을 쓰고 있습니다. 그런데 `package.json`에서 이 의존성은 이미 빠졌습니다. 그래서 JWT 미들웨어로 바꾸기 전에는 새로 설치한 환경에서 모듈 로드 오류가 납니다. 이 내용은 ADR의 Risks와 Implementation 체크리스트에 넣었습니다.

**되돌리는 방법:** `git checkout HEAD -- package.json` 한 번이면 됩니다. HEAD의 `src/auth.js`는 세션 방식 그대로라 코드는 따로 고칠 필요가 없습니다(Reversibility 섹션).
