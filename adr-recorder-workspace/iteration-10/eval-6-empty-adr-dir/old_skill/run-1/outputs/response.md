ADR을 작성했습니다: `docs/adr/001-api-auth-express-session-to-jwt.md`

`docs/adr/`에는 `.gitkeep`만 있고 기존 ADR이 없었습니다. 그래서 번호를 **001**부터 시작했습니다.

**요약**
- **Status:** Proposed (새로 내린 결정이라 코드가 이미 바뀌었어도 Proposed로 시작)
- **Decision:** API 인증을 express-session 쿠키 세션에서 jsonwebtoken 기반 JWT로 전환
- **Decision Source:** Human
- **Alternatives:** 말씀하신 두 가지만 넣었습니다.
  - express-session 쿠키 세션 유지: 파트너사 서버 연동에 쿠키 기반이 번거로워서 기각
  - 세션 유지 + 파트너용 API 키 발급: 키 회전 관리를 따로 만들어야 해서 기각
- Evidence(측정 수치 없음), Recheck if, Review Trigger(재검토 조건이 대화에 없음)는 넣지 않았습니다.

**확인된 사항 (ADR의 Risks와 Implementation에 반영)**
- `package.json`에서는 express-session이 빠졌습니다. 하지만 `src/auth.js`는 아직 `require('express-session')`을 호출합니다. 지금 상태로 설치하고 실행하면 모듈 로드에 실패합니다. JWT 검증 미들웨어로 바꾸는 작업이 남아 있습니다.
- 현재 `SESSION_SECRET`을 쓰는 자리에 들어갈 JWT 서명 키를 어디에 보관하고 어떻게 교체할지 아직 정해지지 않아서, Risks에 적었습니다.

`docs/adr/` 밖의 파일은 수정하지 않았습니다.
