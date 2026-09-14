# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway의 API 인증 방식을 express-session 기반 쿠키 세션에서 jsonwebtoken 기반 JWT로 바꾼다.
- **Scope:** partner-gateway / API 인증 (`src/auth.js`)
- **Decision Source:** Human

---

## Context

### Problem

partner-gateway의 API 인증은 현재 `express-session` 쿠키 세션으로 되어 있다(`src/auth.js`, `SESSION_SECRET` 사용). 파트너사 서버들이 API에 붙기 시작하면서 쿠키 기반 인증이 서버 간 호출에서 번거로워졌다.

### Constraints

- 주요 신규 호출자는 브라우저가 아니라 파트너사 서버다(서버 간 호출).
- 파트너별 키 회전 관리 체계를 따로 만들지 않는 방향을 전제로 한다(API 키 대안 기각 사유).

## Decision

### Selected

- **Technology:** `jsonwebtoken` ^9.0.2 (`express-session` ^1.18.0 제거)
- **Architecture:** 서버 측 세션 저장소와 쿠키에 기대는 방식에서, 요청마다 토큰을 검증하는 방식으로 인증을 전환
- **Implementation:** `package.json`에서 `express-session`을 빼고 `jsonwebtoken`을 추가함(미커밋). 인증 미들웨어(`src/auth.js`)는 아직 세션 방식 그대로임

## Rationale

1. 파트너사 서버에서 호출할 때 쿠키 세션을 유지·전달하는 방식이 번거롭다. 토큰 방식이면 이 부담이 없다.
2. 세션을 유지한 채 파트너용 API 키를 발급하는 안과 달리 키 회전 관리를 따로 만들지 않아도 된다.

## Alternatives

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 express-session 쿠키 세션 인증을 그대로 유지할 수 있음
- **Cons:** 파트너용 API 키의 키 회전 관리를 따로 만들어야 함
- **Rejected because:** 키 회전 관리 기능을 별도로 구축해야 하는 부담
- **Recheck if:** 키 회전 관리를 별도 구축 없이 해결할 수단이 생기는 경우(예: 해당 기능을 제공하는 도구·인프라 도입)

## Consequences

### Positive

- 파트너사 서버가 쿠키 세션 없이 API를 호출할 수 있다.
- 파트너용 API 키 회전 관리를 별도로 구축하지 않아도 된다.

### Negative

- 인증 미들웨어와 비밀값 설정(`SESSION_SECRET` → JWT 서명 키)을 새로 구성해야 한다.
- 세션과 달리 서버에서 발급한 토큰을 만료 전에 무효화하려면 별도 장치가 필요하다.

### Risks

- `src/auth.js`가 여전히 `require('express-session')`을 하고 있어, 의존성 제거 상태로 설치·배포하면 서버가 모듈을 찾지 못해 기동에 실패한다. 미들웨어 교체를 같이 반영해야 한다.
- 토큰 만료 시간, 서명 키 관리 방식이 아직 정해지지 않았다. 토큰이 유출되면 만료 전까지 악용될 수 있다.

## Implementation

- [x] `package.json`: `express-session` 제거, `jsonwebtoken` ^9.0.2 추가
- [ ] 구현 작업: `src/auth.js`의 express-session 미들웨어를 jsonwebtoken 기반 토큰 검증 미들웨어로 교체
- [ ] 테스트: 파트너 주문 조회 API 등 인증이 필요한 경로에서 토큰 검증 동작 확인
- [ ] 모니터링: 토큰 검증 실패(만료·서명 오류) 로깅
- [ ] 문서/설정 업데이트: `SESSION_SECRET`을 대체할 JWT 서명 키 환경변수 설정, 파트너 연동 방식 안내

## Reversibility

- **Reversible:** Yes
- **Rollback:** `git checkout HEAD -- package.json`으로 `express-session` 의존성을 복원한다. 현재 `src/auth.js`는 아직 세션 방식이라 코드 롤백은 필요 없다. 파트너가 JWT 방식으로 연동한 뒤에는 파트너 측 변경도 함께 되돌려야 한다.
- **Migration Cost:** Low

## Review Trigger

- 키 회전 관리를 별도 구축 없이 해결할 수단이 생기는 경우(예: 해당 기능을 제공하는 도구·인프라 도입) → 세션 유지 + 파트너용 API 키 발급 안을 재검토

## References

- **Documentation:** `package.json`(미커밋 변경: express-session 제거, jsonwebtoken 추가), `src/auth.js`, 관련 커밋 `2de7403`(feat: 파트너 주문 조회 API)
