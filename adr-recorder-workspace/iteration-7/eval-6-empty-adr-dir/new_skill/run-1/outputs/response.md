ADR을 작성했습니다: `docs/adr/001-api-auth-session-to-jwt.md`

- `docs/adr/`에 `.gitkeep`만 있고 기존 ADR이 없어서 **001번**으로 시작했습니다.
- **Status: Proposed**로 두었습니다. package.json은 이미 바뀌었지만, 새로 내리는 결정이라 Proposed에서 시작합니다.
- **Alternatives**에는 말씀하신 두 가지를 정리했습니다.
  - 현행 유지(쿠키 세션): 파트너 서버 연동에서 번거로워서 기각
  - 세션 유지 + 파트너용 API 키: 키 회전 관리를 따로 만들어야 해서 기각
  - 대안을 다시 검토할 조건(Recheck if)은 말씀하신 게 없어서 넣지 않았습니다. 그래서 Review Trigger 섹션도 없습니다.
- 측정 수치가 없어 Evidence 섹션은 넣지 않았습니다.

**확인이 필요한 점:** `src/auth.js`가 아직 `require('express-session')`을 쓰고 있습니다. package.json에서 express-session을 뺐기 때문에 새로 `npm install`하면 서버가 시작되지 않습니다. 이 스킬은 `docs/adr/` 밖의 파일을 고치지 않으므로 `src/auth.js`는 그대로 두었습니다. ADR의 Risks와 Implementation 체크리스트에 적어 두었습니다.
