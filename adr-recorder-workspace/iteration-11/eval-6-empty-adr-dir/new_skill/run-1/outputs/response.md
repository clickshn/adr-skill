ADR을 작성했습니다: `docs/adr/001-jwt-api-auth.md`

- `docs/adr/`에 기존 ADR이 없어서(`.gitkeep`만 있음) 001번으로 시작했습니다.
- **Status:** Proposed. 새로 내린 결정이라 코드가 이미 바뀌어 있어도 Proposed로 뒀습니다.
- **Decision Source:** Human. 직접 말씀하신 결정이라 Confidence 필드는 뺐습니다.
- **Alternatives:** ① express-session 쿠키 세션 유지(현행): 파트너 서버 연동이 번거로워서 기각. ② 세션 유지 + 파트너용 API 키 발급: 키 회전 관리를 따로 만들어야 해서 기각.
- 말씀하신 재검토 조건이 없어서 Recheck if와 Review Trigger 섹션은 넣지 않았습니다. 측정 수치도 없어서 Evidence 섹션도 뺐습니다.

**확인이 필요한 점:** `src/auth.js`가 아직 `require('express-session')`을 호출합니다. `package.json`에서 express-session을 뺀 지금 상태로는 설치 후 서버를 띄울 때 모듈 로드가 실패합니다. 이 내용은 ADR의 Risks와 Implementation 항목에 적어 뒀고, 코드는 수정하지 않았습니다.
