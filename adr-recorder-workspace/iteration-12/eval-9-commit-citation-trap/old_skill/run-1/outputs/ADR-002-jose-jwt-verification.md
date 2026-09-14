# ADR-002: JWT 검증 라이브러리를 jose로 교체

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** account-api의 JWT 검증을 jsonwebtoken에서 jose로 교체한다.
- **Scope:** account-api / 인증(src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

account-api는 액세스 토큰 검증에 `jsonwebtoken`을 사용해 왔다(`jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['HS256'] })`).
JWT 검증 라이브러리를 `jose`로 교체하기로 했고, 그 결정을 기록으로 남긴다.

### Constraints

- 기존 토큰 서명 방식(HS256, `JWT_SECRET` 기반 대칭키)은 그대로 유지한다.
- 프로젝트가 ESM(`package.json`의 `"type": "module"`)이라 교체 라이브러리도 ESM에서 동작해야 한다.
- `verifyToken`의 반환 형태(검증된 payload)는 호출부 호환을 위해 유지한다.

## Decision

### Selected

- **Technology:** `jose` ^5.9.6 (기존 `jsonwebtoken` ^9.0.2 제거)
- **Architecture:** 인증 경로의 토큰 검증 지점은 `src/auth.js`의 `verifyToken` 하나로 유지한다. 라이브러리만 교체하고 검증 지점 구조는 바꾸지 않는다.
- **Implementation:** `jose`의 `jwtVerify`를 사용한다. `JWT_SECRET`을 `new TextEncoder().encode(...)`로 `Uint8Array` 키로 변환해 모듈 로드 시 한 번 생성하고, `verifyToken`은 `async` 함수가 되어 `{ payload }`에서 payload를 반환한다. 알고리즘 제한(`algorithms: ['HS256']`)은 동일하게 명시한다.

## Rationale

1. 사용자가 jose 채택을 명시적으로 결정했으며, 의존성과 구현이 이미 해당 결정대로 반영되어 있다(`package.json`, `src/auth.js`).
2. 프로젝트가 ESM 기반이고 `jose`는 ESM/WebCrypto 기반 API를 제공해, 별도 상호운용 처리 없이 그대로 import된다.
3. 검증 알고리즘을 `HS256`으로 계속 고정해 알고리즘 혼동(alg confusion) 계열 위험을 교체 전과 동일하게 차단한다.

## Consequences

### Positive

- 인증 의존성이 `jose` 하나로 정리되고, 검증 로직이 표준 WebCrypto 키 타입 위에서 동작한다.
- 검증 지점이 `verifyToken` 한 곳뿐이라 교체 범위가 작고 추적이 쉽다.

### Negative

- `verifyToken`이 동기 함수에서 `async`로 바뀌어, 앞으로 추가되는 호출부는 반드시 `await`해야 한다. 현재 저장소에는 `src/auth.js` 외 호출부가 없어 이번 변경으로 깨진 곳은 없다.
- 검증 실패 시 던져지는 에러 타입이 `jsonwebtoken`(`TokenExpiredError` 등)과 달라, 에러 타입으로 분기하는 코드를 추가할 때 기준이 바뀐다.

### Risks

- `await` 누락 시 `verifyToken`이 항상 truthy한 Promise를 반환해, 검증 실패가 인증 통과처럼 보일 수 있다. 호출부 추가 시 주의가 필요하다.
- 교체 커밋(`f4dcf2f`)에 JWT 검증 관련 테스트가 포함되어 있지 않아, 만료·서명 위조 토큰에 대한 동작이 회귀 테스트로 보호되지 않는다.

## Implementation

- [x] 구현 작업 (`src/auth.js`를 `jwtVerify` 기반으로 교체, `package.json` 의존성 교체)
- [ ] 테스트 (정상/만료/서명 불일치 토큰에 대한 `verifyToken` 테스트 추가)
- [ ] 모니터링 (토큰 검증 실패율 추적)
- [ ] 문서/설정 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `src/auth.js`를 `jsonwebtoken`의 `jwt.verify` 기반 동기 구현으로 되돌리고 `package.json`의 `jose`를 `jsonwebtoken`으로 교체한다. 변경이 `f4dcf2f` 한 커밋에 모여 있어 해당 커밋의 두 파일 변경을 되돌리면 된다(같은 커밋에 포함된 express 버전 범위 변경은 분리 필요). 토큰 서명 방식과 `JWT_SECRET`이 그대로라 기존 발급 토큰은 롤백 후에도 유효하다.
- **Migration Cost:** Low

## References

- **Documentation:**
  - 실제 교체 커밋: `f4dcf2f` ("chore: dependency bump") — `package.json`, `src/auth.js` 변경 포함
  - 변경 파일: `package.json`, `src/auth.js`
  - 참고: `e187d04` ("feat: switch to jose for JWT verification")은 메시지와 달리 변경 파일이 없는 빈 커밋이라 근거로 인용하지 않는다.
