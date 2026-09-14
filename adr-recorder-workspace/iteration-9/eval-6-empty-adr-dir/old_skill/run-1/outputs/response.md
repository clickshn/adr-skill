ADR을 만들었습니다: `docs/adr/001-api-auth-session-to-jwt.md`

- `docs/adr/`에는 `.gitkeep`만 있고 기존 ADR이 없어서 **001번**부터 시작했습니다.
- **Status: Proposed**로 두었습니다. package.json은 이미 바뀌었지만 새로 내리는 결정이라 Proposed에서 시작합니다.
- **Decision Source: Human**이라 Confidence 필드는 생략했습니다. 측정 수치가 없어서 Evidence 섹션도 넣지 않았습니다.
- **Alternatives**에는 말씀하신 "세션 유지 + 파트너용 API 키 발급"을 넣었습니다. 기각 사유는 "키 회전 관리를 따로 만들어야 함"입니다. Review Trigger는 이 대안의 Recheck if 조건으로 채웠습니다.
- **Reversibility**: `git checkout HEAD -- package.json`으로 되돌릴 수 있습니다(Yes / Low). 다만 파트너사들이 JWT로 연동한 뒤에 되돌리면 비용이 커진다고 적어 두었습니다.

확인이 필요한 점이 하나 있습니다. `src/auth.js`가 아직 `require('express-session')`으로 세션 미들웨어를 만들고 있습니다. package.json에서 express-session을 뺐기 때문에, 이 상태로 의존성을 새로 설치하면 앱이 시작될 때 모듈 로드에 실패합니다. 이 내용은 ADR의 Risks와 Implementation 체크리스트에 넣었습니다. `src/auth.js`는 이 스킬의 수정 범위(docs/adr/) 밖이라 건드리지 않았습니다.
