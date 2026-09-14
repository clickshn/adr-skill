ADR을 작성했습니다: `docs/adr/001-api-auth-session-to-jwt.md`

`docs/adr/`에는 `.gitkeep`만 있고 기존 ADR이 없어서 번호를 **001**부터 시작했습니다.

**내용 요약**
- **Decision:** partner-gateway API 인증을 express-session 쿠키 세션에서 jsonwebtoken 기반 JWT로 교체 (package.json diff 기준: `express-session ^1.18.0` → `jsonwebtoken ^9.0.2`)
- **Context:** 파트너사 서버 연동에서 쿠키 기반 세션이 번거로움. 현재 `src/auth.js`는 세션 store 설정이 없어 기본 MemoryStore를 쓰고 있음
- **Alternatives:** 세션 유지 + 파트너용 API 키 발급. 키 회전 관리를 따로 만들어야 해서 기각. 키 발급·회전을 대신 처리할 수단이 생기면 재검토하도록 Review Trigger에 넣었습니다
- **Decision Source:** Human (말씀해 주신 결정이라 Confidence는 생략)
- **Status:** Proposed. 확정된 결정으로 두시려면 Accepted로 바꾸시면 됩니다
- Evidence 섹션은 측정 수치가 없어서 넣지 않았습니다

**확인이 필요한 점**
`package.json`에서는 express-session을 뺐는데, `src/auth.js`는 아직 `require('express-session')`을 하고 있습니다. 이대로 의존성을 다시 설치하면 앱 기동 시 모듈 로드 오류가 납니다. ADR의 Risks와 Implementation 체크리스트에 적어 두었고, `src/auth.js`는 수정하지 않았습니다. 이 스킬은 `docs/adr/` 밖의 파일은 건드리지 않습니다.
