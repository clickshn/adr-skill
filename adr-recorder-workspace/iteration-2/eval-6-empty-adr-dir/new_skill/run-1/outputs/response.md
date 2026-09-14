변경 내용은 확인했어요. `package.json`에서 `express-session`이 빠지고 `jsonwebtoken ^9.0.2`가 들어갔네요. 대화에서 결정과 기각한 대안도 나와서 ADR 내용은 바로 쓸 수 있어요.

그런데 파일을 만들기 전에 번호를 하나 정해야 해요.

- `docs/adr/`를 확인해 보니 `.gitkeep`만 있고 ADR 파일은 하나도 없어요.
- 이 디렉터리는 이번에 만든 게 아니라 `e7deb89` 커밋("partner-gateway 초기 구성, docs/adr 디렉터리 추가")에서 이미 들어온 거예요.
- 그래서 ADR을 다른 곳(다른 저장소, 위키 등)에서 관리하다 옮겨오는 중일 수도 있어요. 이 경우 번호를 멋대로 정하면 기존 번호와 겹칠 수 있어서 제가 정하지 않았어요.

**이 저장소의 첫 ADR로 `ADR-001`을 쓰면 될까요? 아니면 이어서 매길 기존 번호가 있나요?** 번호만 알려주시면 `docs/adr/`에 파일을 바로 만들게요.

참고로 이렇게 쓸 예정이에요.

- **제목:** API 인증을 express-session 쿠키 세션에서 JWT로 전환
- **Status:** Proposed · **Date:** 2026-09-11 · **Decision Source:** Human (Confidence 생략)
- **Scope:** partner-gateway API 인증
- **Context:** 파트너사 서버가 붙으면서 서버 간 호출에서 쿠키 기반 세션을 다루기가 번거로워짐
- **Decision:** `express-session`을 없애고 `jsonwebtoken` 기반 JWT 인증으로 전환
- **Alternatives:** 세션 방식을 유지하면서 파트너용 API 키를 따로 발급하는 방안
  - 기각 사유: 키 회전 관리 기능을 따로 만들어야 함
- **Review Trigger:** 해당 대안의 Recheck if 조건만 모아서 작성
- **Evidence:** 실측 수치가 없어서 생략
