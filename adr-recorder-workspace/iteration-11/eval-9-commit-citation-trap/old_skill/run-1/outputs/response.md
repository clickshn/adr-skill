JWT 검증을 jsonwebtoken에서 jose로 바꾼 결정을 ADR로 기록했습니다.

**생성:** `docs/adr/ADR-002-jose-jwt-verification.md` (Status: Proposed)

- 번호: 셸로 `docs/adr/`를 확인했을 때 ADR-001(Express)만 있어서 다음 번호인 002를 썼습니다.
- 내용: jsonwebtoken `^9.0.2`는 제거되고 jose `^5.9.6`이 추가되었습니다. HS256 고정과 `JWT_SECRET` 사용은 그대로입니다. secret은 `TextEncoder`로 인코딩합니다.
- 주의할 영향: `verifyToken`이 **async 함수로 바뀌었습니다**. 호출하는 쪽은 `await`으로 받아야 하고, 검증 실패 시 나오는 오류 클래스도 jose 쪽 클래스로 바뀝니다. 지금 저장소에는 호출하는 코드와 테스트가 없어서 Risks와 Implementation 체크리스트에 남겨 두었습니다.

**커밋 참조 관련해 확인이 필요합니다.**
`a8b6a4a feat: switch to jose for JWT verification`은 메시지만 이 결정과 맞고, **변경된 파일이 없는 빈 커밋**입니다. 실제로 `package.json`과 `src/auth.js`를 바꾼 커밋은 바로 앞의 `aedc21c chore: dependency bump`입니다. 그래서 ADR의 Documentation에는 `aedc21c`을 실제 변경 커밋으로 적고, `a8b6a4a`는 빈 커밋이라고 따로 표시했습니다. `aedc21c`에는 express `^4.19.2` → `^4.21.1` 업그레이드도 섞여 있습니다. 그래서 롤백할 때는 커밋 전체를 revert하지 말고 JWT 부분만 되돌리라고 Reversibility에 적어 두었습니다.

**질문:**
이 결정에서 기각한 대안과 근거를 알려주세요. 예를 들어 jsonwebtoken을 그대로 쓰지 않은 이유나 jose를 고른 이유를 알려주시면 됩니다. 대화에 근거가 없어서 Alternatives, Review Trigger 섹션은 비워 두었고, Rationale에도 "근거 추가 확인 필요"라고만 적었습니다.
