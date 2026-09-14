ADR을 작성했습니다.

**`docs/adr/`에 `.gitkeep`만 있고 기존 ADR 파일이 없어서 번호를 001부터 시작했습니다.**

생성한 파일:
- `docs/adr/001-api-auth-jwt.md` — ADR-001: API 인증을 쿠키 세션에서 JWT로 전환

작성하면서 확인한 것 두 가지를 같이 알려드립니다.

1. **Status는 Proposed입니다.** `package.json`은 이미 바뀌었지만 새로 내리는 결정이라 Proposed로 시작합니다.
2. **`src/auth.js`가 아직 `express-session`을 `require`합니다.** `package.json`에서는 의존성이 빠져 있어서 현재 상태 그대로는 모듈을 찾지 못합니다. ADR의 Risks와 Implementation에 남겨뒀습니다.

대안은 대화에서 말씀하신 "세션 유지 + 파트너용 API 키 발급"(키 회전 관리 부담으로 기각) 하나만 정리했고, 재검토 조건은 말씀하신 게 없어서 Recheck if와 Review Trigger는 넣지 않았습니다.

참고로 최근 커밋 `2a29f15 feat: 파트너 주문 조회 API`는 실제 파일 변경이 없는 빈 커밋이라 근거로 인용하지 않았습니다.
