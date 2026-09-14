# ADR-002: JWT 검증 라이브러리를 jsonwebtoken에서 jose로 교체

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** account-api의 JWT 검증을 jsonwebtoken(`jwt.verify`)에서 jose(`jwtVerify`)로 교체한다.
- **Scope:** account-api / 인증 모듈(src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

account-api는 `src/auth.js`의 `verifyToken()`에서 jsonwebtoken `^9.0.2`의 `jwt.verify`로 JWT를 검증하고 있었다. 사용자가 이 검증 로직을 jose로 교체했다고 밝혔고, 코드도 이미 바뀌어 있다. 교체 동기는 대화에서 언급되지 않았다.

### Constraints

- 토큰은 환경변수 `JWT_SECRET` 기반 대칭키(HS256)로 서명되어 있으므로, 교체 후에도 같은 비밀키와 알고리즘으로 검증할 수 있어야 한다.
- 프로젝트는 ESM(`"type": "module"`)으로 구성되어 있다.

## Decision

### Selected

- **Technology:** jose `^5.9.6` (jsonwebtoken `^9.0.2`는 dependencies에서 제거)
- **Architecture:** 인증 모듈 내부의 라이브러리만 교체한다. 검증 방식(HS256 대칭키, `JWT_SECRET`)은 그대로 둔다.
- **Implementation:** `JWT_SECRET`을 `TextEncoder`로 `Uint8Array` 키로 변환하고, `jwtVerify(token, secret, { algorithms: ['HS256'] })`로 검증한 뒤 `payload`를 반환한다. 이 과정에서 `verifyToken()`이 동기 함수에서 `async` 함수(Promise 반환)로 바뀌었다.

## Rationale

1. 사용자가 JWT 검증을 jose로 교체했다고 명시했다. 교체 동기는 대화에 없으므로 여기서는 코드로 확인되는 사실만 적는다.
2. 교체 후에도 알고리즘 허용 목록(`['HS256']`)과 `JWT_SECRET` 기반 검증을 유지하므로, 기존에 발급된 토큰과 호환된다.

## Consequences

### Positive

- JWT 검증 의존성이 jose 하나로 정리되었다(jsonwebtoken 제거).
- 알고리즘 허용 목록을 명시적으로 유지해, 알고리즘 혼동 공격에 대한 방어 수준이 이전과 같다.

### Negative

- `verifyToken()`이 Promise를 반환하므로 모든 호출부가 `await`(또는 `.then`)을 써야 한다. 현재 저장소에는 `src/auth.js` 밖의 호출부가 없지만, 앞으로 동기 호출을 전제로 작성된 코드가 생기면 검증을 건너뛴 채 Promise 객체를 truthy 값으로 오인할 수 있다.

### Risks

- jose는 jsonwebtoken과 오류 타입이 다르다(예: `TokenExpiredError`/`JsonWebTokenError` 대신 `JWTExpired`/`JWSSignatureVerificationFailed` 등). 오류 이름으로 분기하는 코드가 추가되면 새 타입에 맞춰야 한다.
- 저장소에 인증 테스트가 없어서, 교체 전후 동작이 같은지(만료·서명 불일치·알고리즘 불일치 처리) 자동으로 확인되지 않았다.

## Implementation

- [x] 구현 작업: `package.json` 의존성 교체, `src/auth.js`를 `jwtVerify`로 변경 (커밋 aedc21c)
- [ ] 테스트: 유효/만료/서명 불일치/비허용 알고리즘 토큰에 대한 `verifyToken()` 테스트 추가
- [ ] 모니터링: 배포 후 인증 실패율 변화 확인
- [ ] 문서/설정 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`에서 `jose`를 `jsonwebtoken: ^9.0.2`로 되돌리고 `src/auth.js`를 `jwt.verify` 기반 동기 함수로 복원한다. aedc21c에는 express `^4.19.2`→`^4.21.1` 상향도 함께 들어 있으므로, 커밋 전체를 `git revert`하지 말고 JWT 관련 변경만 되돌린다.
- **Migration Cost:** Low

## References

- **Documentation:** 커밋 aedc21c (`chore: dependency bump`). `git show --stat`으로 이 커밋에 `package.json`(jsonwebtoken→jose)과 `src/auth.js`(jwtVerify 전환) 변경이 들어 있음을 확인했다.
