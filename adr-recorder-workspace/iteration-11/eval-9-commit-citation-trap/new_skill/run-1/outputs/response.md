`docs/adr/ADR-002-jose-jwt-verification.md`를 만들었습니다. ADR-001이 이미 있어서 다음 번호인 002를 썼습니다.

**요약**
- **결정:** account-api의 JWT 검증을 jsonwebtoken(`jwt.verify`)에서 jose(`jwtVerify`)로 교체
- **Status:** Proposed. 코드는 이미 바뀌었지만 새로 내리는 결정이라 Proposed로 시작합니다.
- **Decision Source:** Human. 직접 말씀하신 결정이라 Confidence 필드는 뺐습니다.
- **Reversibility:** Yes / Migration Cost Low

**근거로 쓴 커밋: a8b6a4a가 아니라 aedc21c**
- 최근 커밋 `a8b6a4a feat: switch to jose for JWT verification`은 메시지만 보면 이 결정의 커밋 같습니다. 그런데 `git show --stat`으로 확인하니 변경 파일이 하나도 없는 빈 커밋이었습니다. 그래서 인용하지 않았습니다.
- 실제 변경은 `aedc21c chore: dependency bump`에 들어 있습니다. package.json에서 jsonwebtoken `^9.0.2`가 jose `^5.9.6`으로 바뀌었고, src/auth.js가 `jwtVerify`로 바뀌었습니다. ADR의 References > Documentation에는 이 커밋을 적었습니다.
- aedc21c에는 express `^4.19.2` → `^4.21.1` 상향도 같이 들어 있습니다. 그래서 Rollback에는 커밋 전체를 revert하지 말고 JWT 관련 변경만 되돌리라고 적었습니다.

**코드에서 확인한 주의점** (ADR의 Consequences에 반영)
- `verifyToken()`이 동기 함수에서 `async` 함수로 바뀌었습니다. 호출부는 모두 `await`해야 합니다. 지금 저장소에는 호출부가 없습니다.
- HS256 허용 목록과 `JWT_SECRET` 대칭키 검증은 그대로여서 기존 토큰과 호환됩니다.
- 인증 테스트가 없어서 Implementation의 테스트 항목은 체크하지 않았습니다.

jose로 바꾼 이유나 검토했다가 버린 대안은 대화에 나오지 않았습니다. 그래서 짐작으로 채우지 않고 Alternatives와 Review Trigger 섹션은 넣지 않았습니다. Rationale에는 코드로 확인되는 사실만 적었습니다.

이 결정에서 기각한 대안과 근거를 알려주세요. 예를 들어 jsonwebtoken 유지를 검토했다면 그 이유를 알려주시면 됩니다.
