# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway의 API 인증을 express-session 쿠키 세션에서 jsonwebtoken 기반 JWT로 교체한다.
- **Scope:** partner-gateway / API 인증 (src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

파트너사 서버들이 API에 연동되기 시작하면서 쿠키 기반 세션 인증이 번거로워졌다. 현재 인증은 src/auth.js에서 express-session 미들웨어(`SESSION_SECRET`, `resave: false`, `saveUninitialized: false`)로 구성되어 있다.

### Constraints

- 파트너사 서버가 쿠키 기반 세션 없이 호출할 수 있는 인증 방식이어야 한다.
- 파트너용 자격 증명의 키 회전 관리 체계를 별도로 구축하지 않는 범위에서 해결한다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 서버 측 세션 대신, 요청에 포함된 JWT를 서버가 검증하는 토큰 기반(stateless) 인증
- **Implementation:** package.json 의존성 교체는 작업 트리에 반영됨(미커밋). src/auth.js는 아직 express-session 미들웨어이므로 JWT 검증 미들웨어로 교체가 필요하다.

## Rationale

1. 파트너사 서버가 붙는 상황에서 쿠키 기반 세션은 번거롭다. JWT는 쿠키 없이 요청마다 인증 정보를 실어 보낼 수 있다.
2. 세션을 유지하면서 파트너용 API 키를 따로 발급하는 방안과 달리, 키 회전 관리 체계를 별도로 만들 필요가 없다.

## Alternatives

### express-session 세션 유지 + 파트너용 API 키 발급

- **Pros:** 기존 세션 인증 흐름을 그대로 유지할 수 있다.
- **Cons:** 파트너용 API 키의 회전 관리를 따로 만들어야 하고, 세션과 API 키 두 가지 인증 방식을 함께 운영해야 한다.
- **Rejected because:** 키 회전 관리를 별도로 구축해야 해서 접었다.
- **Recheck if:** 키 회전 관리를 직접 만들지 않아도 되는 수단(예: 키 발급·회전을 제공하는 외부 서비스나 게이트웨이)을 쓸 수 있게 되는 경우

## Consequences

### Positive

- 파트너사 서버가 쿠키 처리 없이 API를 호출할 수 있다.
- 서버 측 세션 저장에 의존하지 않는다.

### Negative

- 세션과 달리 발급된 토큰을 서버에서 즉시 무효화하기 어렵다. 만료 시간을 짧게 잡거나 차단 목록 같은 별도 장치가 필요하다.
- 기존에 쿠키 세션으로 인증하던 클라이언트가 있다면 토큰 방식으로 옮겨야 한다.

### Risks

- 현재 작업 트리에서 src/auth.js는 package.json에서 빠진 express-session을 여전히 require한다. 이 상태로 새로 설치하면 서버 시작 시 모듈을 찾지 못해 실패하므로, auth.js를 교체하기 전에 커밋하거나 배포하면 안 된다.
- API 키 회전은 피했지만 JWT 서명 키는 여전히 교체 절차가 필요하다. 서명 키가 유출되면 모든 토큰을 위조할 수 있다.

## Implementation

- [x] package.json: express-session 제거, jsonwebtoken 추가 (작업 트리 반영, 미커밋)
- [ ] 구현 작업: src/auth.js를 express-session 미들웨어에서 JWT 검증 미들웨어로 교체하고 파트너용 토큰 발급 경로 마련
- [ ] 테스트: 유효·만료·위조 토큰과 토큰 누락 시 인증 결과 확인
- [ ] 모니터링: 토큰 검증 실패 추이 확인
- [ ] 문서/설정 업데이트: `SESSION_SECRET` 환경변수를 JWT 서명 키 설정으로 대체하고 파트너 연동 가이드에 토큰 사용법 명시

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json의 jsonwebtoken을 express-session ^1.18.0으로 되돌리고(현재는 미커밋이므로 `git checkout HEAD -- package.json`), src/auth.js를 c398cfc 시점의 express-session 구성으로 복원한다. 파트너 서버가 JWT로 연동한 뒤라면 파트너 측 인증 방식도 함께 되돌려야 한다.
- **Migration Cost:** Medium

## Review Trigger

- 키 회전 관리를 직접 만들지 않아도 되는 수단(예: 키 발급·회전을 제공하는 외부 서비스나 게이트웨이)을 쓸 수 있게 되면, "세션 유지 + 파트너용 API 키 발급" 안을 다시 검토한다.

## References

- **Documentation:** c398cfc: 기존 express-session 인증(src/auth.js)을 도입한 커밋 (롤백 기준점)
