# ADR-002: JWT 검증 라이브러리를 jose로 교체

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** account-api의 JWT 검증을 jsonwebtoken에서 jose로 교체한다.
- **Scope:** account-api / 인증(src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

account-api는 액세스 토큰 검증에 jsonwebtoken(^9.0.2)을 사용하고 있었고, 검증 로직은 `src/auth.js`의 동기 함수 `verifyToken` 한 곳에 모여 있다. 이 검증 경로를 jose(^5.9.6) 기반으로 옮긴다.

### Constraints

- 패키지가 `"type": "module"`로 선언된 ESM 전용 프로젝트다.
- 서명 알고리즘은 HS256, 시크릿은 환경변수 `JWT_SECRET`으로 고정되어 있다(교체 전후 동일).
- 결정 근거는 대화에서 제시되지 않아, 아래 Rationale은 저장소에서 확인 가능한 사실만 정리한 것이다.

## Decision

### Selected

- **Technology:** jose ^5.9.6 (기존 jsonwebtoken ^9.0.2 제거)
- **Architecture:** 토큰 검증은 `src/auth.js`의 `verifyToken` 단일 진입점을 유지하고, 내부 구현만 `jwtVerify`로 교체한다.
- **Implementation:** `jwtVerify(token, secret, { algorithms: ['HS256'] })` 호출 후 `payload`만 반환한다. 시크릿은 `TextEncoder`로 인코딩한 `Uint8Array`로 전달하며, 함수 시그니처는 동기에서 `async`로 바뀐다.

## Rationale

1. 프로젝트가 ESM 전용(`"type": "module"`)이고, jose는 ESM과 표준 Web Crypto 기반이라 CJS 상호운용 계층 없이 그대로 동작한다.
2. 알고리즘 화이트리스트(`algorithms: ['HS256']`)를 교체 전후 동일하게 유지해, 토큰 포맷·시크릿 운영 방식을 바꾸지 않고 라이브러리만 교체할 수 있었다.
3. 검증 경로가 `verifyToken` 한 함수로 캡슐화되어 있어 교체 범위가 파일 1개(9줄 수정)로 제한된다.

## Consequences

### Positive

- ESM 환경에서 번들러·런타임 상호운용 문제가 줄어든다.
- 검증 실패 시 jose의 구체적 에러 타입(만료, 서명 불일치 등)으로 분기할 여지가 생긴다.
- 토큰 발급 포맷과 시크릿 운영 방식은 변경되지 않아 클라이언트 영향이 없다.

### Negative

- `verifyToken`이 동기에서 `async`로 바뀌어 모든 호출부가 `await`를 붙여야 한다.
- 반환값이 jsonwebtoken의 디코드 결과에서 jose의 `payload`로 바뀌어, 헤더 정보에 의존하던 코드가 있었다면 별도 처리가 필요하다.

### Risks

- 호출부에서 `await`를 누락하면 반환된 Promise가 truthy로 평가되어 검증 실패 토큰이 통과할 수 있다. 인증 미들웨어 전 경로의 `await` 적용 여부 확인이 필요하다.
- 에러 객체 형태가 달라져, jsonwebtoken의 `TokenExpiredError` 등을 이름으로 잡던 예외 처리가 있으면 조용히 동작하지 않을 수 있다.

## Implementation

- [ ] 구현 작업 — `src/auth.js` 교체 완료(커밋 5576d53), `verifyToken` 호출부 전수 확인 필요
- [ ] 테스트 — 유효/만료/서명 불일치/alg 변조 토큰에 대한 검증 테스트
- [ ] 모니터링 — 교체 배포 후 401 비율 변화 관찰
- [ ] 문서/설정 업데이트 — 인증 관련 문서의 라이브러리 명시 갱신

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`의 `jose`를 `jsonwebtoken ^9.0.2`로 되돌리고 `src/auth.js`를 커밋 5576d53 이전 구현(동기 `jwt.verify`)으로 복원한다. 토큰 포맷과 시크릿이 동일해 발급된 토큰은 그대로 유효하다.
- **Migration Cost:** Low

## References

- **Documentation:** 실제 변경 커밋 `5576d53` (chore: dependency bump — package.json, src/auth.js). 메시지가 교체를 가리키는 `77d5c5e` (feat: switch to jose for JWT verification)는 변경 내용이 없는 빈 커밋이라 근거로 인용하지 않았다.
