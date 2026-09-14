ADR을 작성했습니다: `docs/adr/001-api-auth-session-to-jwt.md`

`docs/adr/`에 기존 ADR이 없어서(`.gitkeep`만 있음) 번호는 **001**부터 시작했습니다.

**요약**
- **Status:** Proposed (코드가 이미 바뀌었더라도 새 결정이라 Proposed로 시작합니다)
- **Decision:** partner-gateway API 인증을 express-session 쿠키 세션에서 jsonwebtoken 기반 JWT로 교체
- **Decision Source:** Human
- **Alternatives:** 말씀하신 두 가지만 정리했습니다
  - express-session 쿠키 세션 유지(현행): 파트너사 서버가 붙으면서 쿠키 방식이 번거로워서 기각
  - 세션 유지 + 파트너용 API 키 발급: 키 회전 관리를 따로 만들어야 해서 기각
- 대화에서 재검토 조건을 말씀하지 않으셔서 Recheck if와 Review Trigger는 넣지 않았습니다. 실측 수치가 없어 Evidence 섹션도 뺐습니다.

**저장소에서 확인한 사항**
- `package.json` 변경(express-session 제거, jsonwebtoken ^9.0.2 추가)은 아직 커밋되지 않았습니다.
- `src/auth.js`가 아직 `require('express-session')`으로 세션 미들웨어를 만들고 있습니다. 의존성을 다시 설치하면 모듈을 찾지 못해 서버가 뜨지 않으니, ADR의 Risks와 Implementation 체크리스트에 적어 두었습니다. 이 파일은 ADR 범위 밖이라 건드리지 않았습니다.
