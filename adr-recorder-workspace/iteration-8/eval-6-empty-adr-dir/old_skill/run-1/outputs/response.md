`docs/adr/`에는 `.gitkeep`만 있고 기존 ADR이 없어서 번호는 001부터 시작했습니다.

**생성한 파일:** `docs/adr/001-api-auth-session-to-jwt.md`

- **Status:** Proposed. 새로 내린 결정이라 `package.json`이 이미 바뀌어 있어도 Proposed로 시작합니다.
- **Decision Source:** Human
- **Alternatives:** "세션 유지 + 파트너용 API 키 발급"을 넣었습니다. 키 회전 관리를 따로 만들어야 해서 기각했다는 근거를 그대로 적었고, 재검토 조건은 Review Trigger에도 넣었습니다.
- **Evidence:** 측정 수치가 없어서 섹션을 만들지 않았습니다.

**확인이 필요한 부분:** `src/auth.js`는 아직 `require('express-session')`을 호출합니다. `package.json`에서 의존성을 뺀 상태로 설치하고 배포하면 서버가 모듈을 찾지 못해 뜨지 않습니다. 이 내용은 ADR의 Risks와 Implementation에 적어 두었습니다. `src/auth.js`는 `docs/adr/` 밖에 있는 파일이라 수정하지 않았습니다.
