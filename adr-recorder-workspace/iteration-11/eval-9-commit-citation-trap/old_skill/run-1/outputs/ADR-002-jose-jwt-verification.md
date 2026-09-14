# ADR-002: JWT 검증 라이브러리를 jsonwebtoken에서 jose로 교체

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** account-api의 JWT 검증을 jsonwebtoken(`jwt.verify`)에서 jose(`jwtVerify`)로 교체한다.
- **Scope:** account-api / 인증 (src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

account-api는 `src/auth.js`의 `verifyToken`에서 jsonwebtoken `^9.0.2`의 `jwt.verify`로 JWT를 검증해 왔다. 사용자가 이 검증을 jose로 바꿨다고 밝혔다. 교체를 결정한 구체적인 이유는 대화에 나오지 않았다.

### Constraints

- 서명 알고리즘은 교체 전과 같이 HS256으로 고정한다(`algorithms: ['HS256']`).
- 대칭 키는 여전히 `process.env.JWT_SECRET` 환경변수에서 읽는다. jose는 키로 `Uint8Array`를 받으므로 `TextEncoder`로 인코딩한다.
- 패키지는 ESM(`"type": "module"`)이다. jose는 named import(`import { jwtVerify } from 'jose'`)로 가져온다.

## Decision

### Selected

- **Technology:** jose `^5.9.6` (jsonwebtoken `^9.0.2` 제거)
- **Architecture:** 검증 진입점은 계속 `verifyToken(token)` 하나이며, 반환 방식이 동기에서 비동기(Promise)로 바뀐다.
- **Implementation:** `jwtVerify(token, secret, { algorithms: ['HS256'] })`로 검증하고 `payload`만 반환한다. secret은 모듈 로드 시 `new TextEncoder().encode(process.env.JWT_SECRET)`로 한 번만 인코딩한다.

## Rationale

1. 사용자가 JWT 검증 라이브러리를 jose로 교체하기로 결정했다. 선택의 구체적 근거는 대화에 없어 추가 확인이 필요하다.
2. 교체 후에도 HS256 고정과 `JWT_SECRET` 사용은 그대로여서 토큰 형식과 서명 키를 바꿀 필요가 없다.

## Consequences

### Positive

- 코드베이스에서 JWT 관련 의존성이 jose 하나로 정리되고, jsonwebtoken은 `package.json`에서 제거되었다.
- 알고리즘 허용 목록(HS256)을 명시하는 방식이 유지되어 알고리즘 혼동 방어 수준이 교체 전과 같다.

### Negative

- `verifyToken`이 `async` 함수가 되어 호출부가 반드시 `await`(또는 `.then`)으로 결과를 받아야 한다. 동기 반환을 가정한 코드에서는 페이로드 대신 Promise를 받게 된다. 현재 저장소에는 `verifyToken`을 호출하는 코드가 없다(src/auth.js의 정의만 존재).
- 검증 실패 시 던지는 오류가 jsonwebtoken의 `JsonWebTokenError`/`TokenExpiredError`에서 jose의 오류 클래스(`JWTExpired`, `JWSSignatureVerificationFailed` 등)로 바뀐다. 오류 타입이나 이름으로 분기하는 코드가 있다면 수정해야 한다.

### Risks

- 저장소에 테스트가 없어 교체 전후의 검증 동작(만료, 잘못된 서명, 알고리즘 불일치 거부)이 같은지 확인되지 않았다.
- 같은 커밋(aedc21c)에 express `^4.19.2` → `^4.21.1` 업그레이드가 함께 들어 있다. 이 ADR의 결정과는 별개지만, 커밋 단위로 롤백하면 express 업그레이드도 같이 되돌아간다.

## Implementation

- [x] 구현 작업 — `src/auth.js`를 jose `jwtVerify` 기반으로 교체, `package.json`에서 jsonwebtoken을 jose로 대체
- [ ] 테스트 — 유효 토큰, 만료 토큰, 서명 불일치, HS256 외 알고리즘 토큰 거부 케이스
- [ ] 모니터링 — 배포 후 인증 실패율 변화 확인
- [ ] 문서/설정 업데이트 — `verifyToken`이 비동기로 바뀐 점을 호출부 개발자에게 공유

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`의 `jose`를 `jsonwebtoken@^9.0.2`로 되돌리고 `src/auth.js`를 `jwt.verify` 기반으로 복구한다. `git revert aedc21c`을 쓰면 express 업그레이드도 함께 되돌아가므로 두 파일의 JWT 부분만 되돌리는 편이 안전하다. 호출부가 `await`을 쓰고 있어도 동기 반환값에 대한 `await`은 그대로 동작한다.
- **Migration Cost:** Low

## References

- **Documentation:** 실제 코드 변경 커밋 `aedc21c` (chore: dependency bump — package.json, src/auth.js). 메시지가 이 결정과 일치하는 `a8b6a4a` (feat: switch to jose for JWT verification)는 변경 파일이 없는 빈 커밋이다.
