ADR을 `docs/adr/001-replace-session-with-jwt.md`에 작성했어요.

`docs/adr/`에 `.gitkeep`만 있고 기존 ADR은 없어서 **ADR-001**부터 번호를 매겼습니다.

**담은 내용**
- **결정:** partner-gateway API 인증을 express-session 쿠키 세션에서 jsonwebtoken 기반 JWT로 바꿈. `package.json` diff에 있는 그대로입니다(express-session `^1.18.0` 제거, jsonwebtoken `^9.0.2` 추가).
- **배경:** 파트너사 서버가 서버 간 호출로 붙으면서 쿠키 기반 흐름이 번거로워짐.
- **기각한 대안:** 세션을 유지하고 파트너용 API 키를 발급하는 방식. 키 회전 관리를 따로 만들어야 해서 기각했습니다. 다시 볼 조건(Review Trigger)은 "키 회전을 기성 기능으로 제공하는 게이트웨이나 시크릿 매니저를 도입할 때"로 적었습니다.
- **Decision Source:** Human이라 Confidence는 넣지 않았어요. 측정 수치가 없어서 Evidence 섹션도 없습니다.
- **Status:** 템플릿 기본값인 Proposed로 뒀어요. 확정됐으면 Accepted로 바꾸시면 됩니다.

**작성하다 발견한 문제**
`src/auth.js`가 아직 `require('express-session')`을 쓰고 있어요. 지금 `package.json`으로 의존성을 새로 설치하면 서버를 띄울 때 모듈을 못 찾아 실패합니다. 이 내용은 ADR의 Risks와 Implementation 체크리스트에 넣었어요. `src/auth.js`는 docs/adr/ 밖이라 건드리지 않았습니다.

`src/auth.js`를 JWT 검증 미들웨어로 바꾸는 작업도 이어서 할까요?
