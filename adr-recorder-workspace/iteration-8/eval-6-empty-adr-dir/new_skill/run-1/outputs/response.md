ADR을 작성했습니다: `docs/adr/001-api-auth-session-to-jwt.md`

- `docs/adr/`에는 `.gitkeep`만 있고 기존 ADR 파일이 없어서 **001번부터 시작**했습니다.
- **Status는 Proposed**입니다. `package.json`은 이미 바뀌었지만, 새로 내리는 결정은 구현 상태와 상관없이 Proposed로 시작합니다.
- 결정을 직접 내리셨기 때문에 Decision Source는 Human이고 Confidence는 넣지 않았습니다.
- Alternatives에는 말씀하신 두 가지를 적었습니다. 하나는 현행 유지(쿠키 세션)로, 파트너 서버 연동이 번거롭다는 사유입니다. 다른 하나는 세션 유지 + 파트너용 API 키 발급으로, 키 회전 관리를 따로 만들어야 한다는 사유입니다.
- 언제 다시 검토할지에 대한 조건은 말씀하신 게 없어서 Recheck if 줄과 Review Trigger 섹션은 넣지 않았습니다. 측정 수치도 없어서 Evidence 섹션도 뺐습니다.

**확인이 필요한 점:** `package.json`에서는 express-session이 빠졌지만 `src/auth.js`는 아직 `require('express-session')`을 쓰고 있습니다. 이대로 의존성을 새로 설치해 배포하면 모듈을 찾지 못해 서버가 뜨지 않습니다. ADR의 Risks와 Implementation에 이 내용을 적어 두었습니다. `src/auth.js`는 `docs/adr/` 밖에 있어서 수정하지 않았습니다. JWT 미들웨어로 바꾸길 원하시면 말씀해 주세요.
