`docs/adr/`에 `.gitkeep`만 있고 기존 ADR 파일이 없어서 **001번**으로 시작했습니다.

생성한 파일: `docs/adr/001-api-auth-session-to-jwt.md`

정리한 내용:

- **Status:** 새로 내리는 결정이라 코드가 이미 바뀌어 있어도 `Proposed`로 시작했습니다.
- **Context:** 파트너사 서버 연동이 늘면서 쿠키 기반 세션이 서버 대 서버 호출에 번거롭다는 배경.
- **Decision:** `jsonwebtoken ^9.0.2` 추가 / `express-session ^1.18.0` 제거 (작업 트리 diff 기준), 무상태 JWT 검증으로 전환.
- **Alternatives:** "세션 유지 + 파트너용 API 키 발급"을 키 회전 관리 부담 때문에 기각한 것으로 기록했습니다.
- **Reversibility:** 아직 커밋 전이라 HEAD(abe4c7c) 기준 되돌리기 가능, Migration Cost는 Low로 봤습니다.

작성 중 확인된 점 하나: `src/auth.js`가 아직 `require('express-session')`을 그대로 쓰고 있습니다. package.json에서 의존성만 빠진 상태라 이 파일을 JWT 검증 미들웨어로 교체하기 전에는 기동이 안 됩니다. ADR의 Risks와 Implementation 체크리스트에 넣어뒀습니다.

재검토 조건(Recheck if)은 말씀에 없어서 넣지 않았고, 그래서 Review Trigger 섹션도 만들지 않았습니다. 나중에 "파트너사가 N곳 넘으면" 같은 조건이 정해지면 추가해 드릴게요.
