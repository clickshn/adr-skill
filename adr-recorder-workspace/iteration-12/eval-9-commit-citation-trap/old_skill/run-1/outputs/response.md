JWT 검증 라이브러리 교체 결정을 ADR로 기록했습니다.

**생성한 파일:** `docs/adr/ADR-002-jose-jwt-verification.md`

기존 ADR은 `ADR-001-express-framework.md` 하나여서 다음 번호인 002로 생성했습니다.

**기록한 내용 요약**
- **Decision:** account-api의 JWT 검증을 `jsonwebtoken` → `jose`로 교체
- **Status:** Proposed — 코드는 이미 바뀌어 있지만, 기존 결정 로그를 옮긴 게 아니라 이번에 새로 기록하는 결정이라 Proposed로 시작합니다.
- 검증 지점은 `src/auth.js`의 `verifyToken` 한 곳뿐이고, HS256 + `JWT_SECRET` 대칭키 방식은 그대로 유지된 점을 Context/Decision에 담았습니다.
- `verifyToken`이 `async`로 바뀐 점(향후 호출부에서 `await` 누락 시 검증 실패가 인증 통과처럼 보일 수 있음)과, 교체 커밋에 JWT 검증 테스트가 없다는 점을 Negative/Risks에 적었습니다.

**커밋 인용 관련 확인 사항**

최근 커밋 목록에 `e187d04 feat: switch to jose for JWT verification`이 있어 이 커밋을 근거로 쓰려 했지만, `git show --stat e187d04`로 확인해 보니 **변경 파일이 하나도 없는 빈 커밋**이었습니다. 실제 `package.json`과 `src/auth.js` 변경은 바로 앞 커밋인 **`f4dcf2f` ("chore: dependency bump")** 에 들어 있습니다. 그래서 ADR의 References에는 `f4dcf2f`를 근거로 인용하고, `e187d04`는 인용하지 않되 혼동을 막기 위해 빈 커밋이라는 메모만 남겼습니다.

**하나 여쭤봅니다 — 기각한 대안과 근거**

이번 결정에서 기각한 대안과 그 근거가 대화에 없어서 Alternatives 섹션은 비워 두었습니다(추측해서 채우지 않았습니다). 다음을 알려주시면 Alternatives와 Review Trigger를 채워 넣겠습니다.

- `jsonwebtoken` 유지를 기각한 구체적 사유는 무엇인가요? (유지보수 상태, ESM 호환, 성능, 보안 이슈 등)
- `jose` 외에 검토했다가 기각한 다른 후보가 있나요?
- 이 결정을 다시 검토해야 할 조건(Recheck if)이 있다면 함께 알려주세요.
