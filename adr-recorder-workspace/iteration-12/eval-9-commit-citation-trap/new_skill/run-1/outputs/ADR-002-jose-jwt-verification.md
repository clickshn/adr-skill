# ADR-002: JWT 검증 라이브러리를 jose로 교체

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** account-api의 JWT 검증을 jsonwebtoken에서 jose로 교체한다.
- **Scope:** account-api (src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

account-api는 토큰 검증에 jsonwebtoken(^9.0.2)을 사용해 왔다. 사용자가 JWT 검증 구현을 jose로 교체하기로 결정했고, 변경은 이미 저장소에 반영되어 있다.

### Constraints

- 기존 검증 알고리즘(HS256)과 `JWT_SECRET` 환경변수 기반 시크릿 구성을 유지해야 한다.
- 프로젝트는 ESM(`"type": "module"`)이며, jose의 `jwtVerify`는 Promise를 반환하므로 `verifyToken`이 async가 된다. 이 함수를 호출하는 쪽은 await가 필요하다.

## Decision

### Selected

- **Technology:** jose ^5.9.6 (jsonwebtoken ^9.0.2 제거)
- **Architecture:** 변경 없음. 토큰 검증은 계속 `src/auth.js`의 `verifyToken` 단일 진입점에서 수행한다.
- **Implementation:** `jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['HS256'] })` → `jwtVerify(token, secret, { algorithms: ['HS256'] })`. 시크릿은 `new TextEncoder().encode(process.env.JWT_SECRET)`로 인코딩하고, `verifyToken`은 async 함수로 바뀌어 payload를 반환한다.

## Rationale

1. 사용자가 JWT 검증 구현을 jose로 전환하기로 결정했다.
2. 검증 알고리즘(HS256)과 시크릿 소스를 그대로 유지해 토큰 호환성을 깨지 않는 최소 변경으로 교체했다.
3. 교체 근거의 세부 사항(어떤 대안을 왜 기각했는지)은 아직 기록되지 않았으며, 확인 후 Alternatives를 보완해야 한다.

## Alternatives

### jsonwebtoken 유지 (현행 유지)

- **Rejected because:** 대화에 기각 사유가 기록되지 않음 — 확인 후 보완 필요.

## Consequences

### Positive

- 검증 로직이 jose의 표준 JWT/JOSE 구현 위에 놓여, 향후 JWK/비대칭 알고리즘 확장 시 같은 라이브러리로 처리할 수 있다.
- 의존성 하나(jsonwebtoken)가 제거되었다.

### Negative

- `verifyToken`이 sync에서 async로 바뀌어, 호출부는 모두 await/Promise 처리를 해야 한다.

### Risks

- 호출부 중 await를 누락한 곳이 있으면 Promise 객체가 payload로 취급되어 인증이 사실상 무력화될 수 있다. 현재 저장소에는 `verifyToken` 호출부가 `src/auth.js` 외에 없고 테스트도 없어, 회귀를 잡아줄 자동 검증 장치가 없다.

## Implementation

- [x] 구현 작업 (`src/auth.js`, `package.json` 변경 완료)
- [ ] 테스트 (현재 저장소에 테스트 파일 및 test 스크립트 없음)
- [ ] 모니터링 (토큰 검증 실패율)
- [ ] 문서/설정 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `git revert f4dcf2f` — jsonwebtoken ^9.0.2와 동기 `verifyToken` 구현이 복원된다. 단 이 커밋은 express ^4.19.2 → ^4.21.1 범프도 함께 담고 있어, 되돌리면 express 버전도 같이 내려간다. JWT 부분만 되돌리려면 `src/auth.js`와 package.json의 해당 줄만 선택 복원한다.
- **Migration Cost:** Low

## References

- **Documentation:** 실제 변경 커밋 f4dcf2f (`chore: dependency bump`) — package.json, src/auth.js 포함. (커밋 e187d04 `feat: switch to jose for JWT verification`은 메시지와 달리 변경 파일이 없는 빈 커밋이라 근거로 인용하지 않았다.)
