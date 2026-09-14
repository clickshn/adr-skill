`docs/adr/ADR-002-jose-jwt-verification.md`를 새로 만들었습니다. 기존에 ADR-001(Express)이 있어 다음 번호인 002로 이어 붙였습니다.

정리한 내용:

- **Decision:** account-api의 JWT 검증을 jsonwebtoken ^9.0.2 → jose ^5.9.6으로 교체. HS256과 `JWT_SECRET` 기반 시크릿은 유지.
- **Implementation:** `jwt.verify(...)` → `jwtVerify(token, new TextEncoder().encode(process.env.JWT_SECRET), { algorithms: ['HS256'] })`, `verifyToken`이 async로 변경.
- **Status:** 코드는 이미 반영돼 있지만 새로 내린 결정이므로 Proposed로 시작했습니다.

커밋 인용에 대해 하나 알려드립니다. 로그에는 `e187d04 feat: switch to jose for JWT verification`이 이 변경처럼 보이지만, `git show --stat e187d04` 결과 **변경 파일이 없는 빈 커밋**이었습니다. 실제로 package.json과 src/auth.js를 바꾼 커밋은 바로 앞의 `f4dcf2f chore: dependency bump`입니다. 그래서 ADR의 References와 Rollback에는 f4dcf2f를 인용했습니다. 참고로 f4dcf2f에는 express ^4.19.2 → ^4.21.1 범프도 함께 들어 있어, 통째로 revert하면 express 버전도 같이 내려갑니다.

한 가지만 확인해 주세요. **이 결정에서 기각한 대안과 근거를 알려주세요.** 지금은 "jsonwebtoken 유지(현행 유지)"만 대안으로 적어두고 기각 사유는 비워둔 상태입니다. 왜 jsonwebtoken을 두고 jose를 골랐는지(또는 검토했던 다른 라이브러리가 있었는지) 알려주시면 Alternatives 섹션을 채우겠습니다. 재검토 조건(Recheck if)이 있다면 그것도 함께 주시면 Review Trigger를 추가하겠습니다.
