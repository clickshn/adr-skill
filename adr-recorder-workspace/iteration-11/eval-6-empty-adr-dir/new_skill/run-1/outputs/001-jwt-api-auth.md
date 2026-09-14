# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** partner-gateway의 API 인증 방식을 express-session 쿠키 세션에서 jsonwebtoken 기반 JWT로 교체한다.
- **Scope:** partner-gateway / API 인증 (`src/auth.js`, `package.json`)
- **Decision Source:** Human

---

## Context

### Problem

- 현재 API 인증은 `src/auth.js`의 express-session 미들웨어(쿠키 세션, `SESSION_SECRET`)로 처리한다.
- 파트너사 서버들이 API에 붙기 시작하면서, 서버 간 호출에서 쿠키 기반 세션을 다루는 것이 번거로워졌다.

### Constraints

- 호출 주체가 브라우저가 아니라 파트너사 서버다(서버 대 서버 연동).
- 파트너 인증용 키 회전 관리 체계를 별도로 만들어 운영하는 부담은 지지 않으려 한다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 쿠키 기반 서버 세션 대신, 요청마다 JWT를 제시하고 서버가 이를 검증하는 토큰 기반 인증
- **Implementation:** `package.json`에서 express-session을 빼고 jsonwebtoken을 추가함(작업 트리 반영, 미커밋). `src/auth.js`는 아직 express-session 미들웨어 그대로다.

## Rationale

1. 파트너사 서버가 쿠키 세션을 유지할 필요 없이 토큰만 실어 호출할 수 있어, 서버 간 연동에서 쿠키 기반 방식의 번거로움이 사라진다.
2. 세션 방식을 유지하면서 파트너용 API 키를 따로 발급하는 방식과 달리, 키 회전 관리 체계를 별도로 만들 필요가 없다.

## Alternatives

### express-session 쿠키 세션 유지 (현행)

- **Pros:** 이미 구성되어 있어 추가 작업이 없다.
- **Cons:** 파트너사 서버가 붙을 때 쿠키 기반 연동이 번거롭다.
- **Rejected because:** 파트너사 서버 연동에서 쿠키 기반 방식이 번거로워서.

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 세션 인증을 그대로 두고 파트너 연동만 API 키로 해결할 수 있다.
- **Cons:** 키 회전 관리를 따로 만들어야 한다.
- **Rejected because:** 키 회전 관리를 따로 만들어야 해서.

## Consequences

### Positive

- 파트너사 서버가 쿠키 없이 토큰으로 API를 호출할 수 있다.
- 서버 측 세션 저장이 필요 없어지고, 인증 방식이 JWT 하나로 정리된다.

### Negative

- 기존 쿠키 세션 기반으로 인증하던 클라이언트는 JWT 방식으로 옮겨야 한다.
- 토큰 발급·검증 로직을 새로 작성해야 한다.

### Risks

- `src/auth.js`가 아직 `require('express-session')`을 호출하므로, 의존성이 빠진 현재 상태로는 설치 후 서버 기동 시 모듈 로드에 실패한다. 인증 미들웨어 교체 전까지 배포하면 안 된다.
- JWT는 발급 후 만료 전까지 서버에서 즉시 무효화하기 어렵다. 만료 시간과 서명 비밀값 관리가 보안 수준을 좌우한다.

## Implementation

- [ ] `src/auth.js`의 express-session 미들웨어를 jsonwebtoken 기반 JWT 검증 미들웨어로 교체
- [ ] 파트너용 JWT 발급 흐름과 서명 비밀값(현 `SESSION_SECRET` 대체) 설정
- [ ] 테스트: 유효/만료/위조 토큰에 대한 인증 동작 확인
- [ ] 모니터링: 인증 실패율 확인
- [ ] 문서/설정 업데이트: 파트너 연동 가이드, 환경 변수

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`에서 jsonwebtoken을 빼고 express-session ^1.18.0을 되돌린 뒤(`git checkout HEAD -- package.json`), `src/auth.js`의 세션 미들웨어를 유지·복원한다. 파트너사가 JWT로 연동한 뒤라면 파트너 측 호출 방식도 되돌려야 한다.
- **Migration Cost:** Low (파트너 JWT 연동 전 기준, 연동 후에는 상승)

## References

- **Documentation:** express-session 도입 커밋 `dbbeb0a` (partner-gateway 초기 구성: `package.json`, `src/auth.js`)
