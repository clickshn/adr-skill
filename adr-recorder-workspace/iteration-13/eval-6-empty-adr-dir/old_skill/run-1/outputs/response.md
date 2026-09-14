ADR 작성했습니다: `docs/adr/001-api-auth-jwt.md`

`docs/adr/`에 `.gitkeep`만 있고 기존 ADR 파일이 없어서 번호는 **001**부터 시작했습니다.

정리한 내용:

- **Decision:** partner-gateway의 API 인증을 express-session 쿠키 세션에서 JWT로 교체
- **Status:** Proposed — 새로 내리는 결정이라 코드/의존성이 이미 바뀌었어도 Proposed로 시작합니다.
- **Alternatives:** 말씀하신 "세션 유지 + 파트너용 API 키 발급"을 기각 사유(키 회전 관리를 따로 구축해야 함)와 함께 기록했습니다.
- **Reversibility:** Yes. 되돌릴 때 기준이 되는 세션 설정 원본은 커밋 `2054636`에 있습니다. 참고로 최신 커밋 `abe4c7c`는 파일 변경이 없는 빈 커밋이라 복원 기준으로 쓰지 않았습니다.

작성하면서 확인한 것 두 가지 알려드립니다:

1. `package.json`에서는 `express-session`이 빠지고 `jsonwebtoken ^9.0.2`가 들어갔는데, `src/auth.js`는 아직 `require('express-session')` 그대로입니다. 이 상태로 설치·기동하면 모듈을 못 찾고 실패하니 코드 교체 전에는 배포하지 마세요. ADR의 Risks에 적어뒀습니다.
2. 측정 수치가 없어서 Evidence 섹션은 만들지 않았고, 재검토 조건을 따로 말씀하신 게 없어서 Recheck if / Review Trigger도 비워뒀습니다. "이런 조건이면 API 키 방식을 다시 본다" 같은 기준이 있으면 알려주세요, 추가하겠습니다.

`src/auth.js`의 JWT 미들웨어 교체까지 이어서 할까요?
