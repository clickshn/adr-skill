`docs/adr/001-api-auth-jwt.md`를 작성했어요.

- **번호:** `docs/adr/`에 `.gitkeep`만 있고 기존 ADR이 없어서 001번부터 시작했어요.
- **Status:** 새로 내린 결정이라 Proposed로 뒀어요. 직접 내린 결정이라 Decision Source는 Human이고, 그래서 Confidence 필드는 뺐어요.
- **대안:** "세션 유지 + 파트너용 API 키"는 키 회전 관리를 따로 만들어야 해서 기각했다고 적었어요. 이걸 다시 검토할 조건(키 관리를 직접 만들 필요가 없어질 때)은 Review Trigger에 넣었어요.
- **Evidence:** 실측 수치가 없어서 섹션을 만들지 않았어요.

**확인이 필요한 점:** `package.json`에서는 `express-session`을 뺐지만 `src/auth.js`는 아직 `require('express-session')`을 하고 있어요. 이대로 새로 설치하면 모듈을 찾지 못해서 앱이 뜨지 않아요. 이 내용은 ADR의 Risks와 Implementation 첫 항목에 적어뒀어요.

토큰 만료 시간, 서명 알고리즘, 파트너에게 토큰을 발급하는 방식은 대화에 나오지 않아서 추측으로 채우지 않았어요.
