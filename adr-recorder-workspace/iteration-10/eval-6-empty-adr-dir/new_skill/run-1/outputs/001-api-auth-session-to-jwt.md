# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway API 인증 방식을 express-session 기반 쿠키 세션에서 jsonwebtoken 기반 JWT로 교체한다.
- **Scope:** partner-gateway (v2.1.0) / API 인증 계층 (`src/auth.js`)
- **Decision Source:** Human

---

## Context

### Problem

파트너사 서버들이 API에 붙기 시작하면서, 서버 간 호출에서 쿠키 기반 세션 인증을 다루는 것이 번거로워졌다. 현재 인증은 `src/auth.js`의 express-session 미들웨어(`SESSION_SECRET` 환경변수 사용)로 구성되어 있다.

### Constraints

- 파트너사 서버(서버 간 호출)가 번거로운 쿠키 처리 없이 인증할 수 있어야 한다.
- 파트너용 키 회전 관리 같은 별도 관리 기능을 새로 만들지 않는 방향을 선호한다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 서버 측 세션 저장 + 쿠키 방식에서, 요청마다 JWT를 제시·검증하는 방식으로 전환
- **Implementation:** `package.json`에서 express-session을 빼고 jsonwebtoken을 추가함(작업 트리 반영, 미커밋). `src/auth.js`는 아직 express-session을 사용하는 상태로 남아 있음.

## Rationale

1. 파트너사 서버가 붙는 상황에서 쿠키 기반 세션은 연동이 번거롭고, JWT는 쿠키에 의존하지 않는다.
2. 세션을 유지하면서 파트너용 API 키를 따로 발급하는 방식은 키 회전 관리를 별도로 만들어야 하므로, 인증 방식을 JWT 하나로 바꾸는 쪽을 택했다.

## Alternatives

### express-session 쿠키 세션 유지 (현행)

- **Pros:** 기존 `src/auth.js` 구성을 그대로 쓸 수 있어 코드 변경이 없다.
- **Cons:** 파트너사 서버 간 호출에서 쿠키 기반 인증이 번거롭다.
- **Rejected because:** 파트너사 서버들이 붙으면서 쿠키 기반 방식이 번거로워졌다.

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 세션 인증을 유지한 채 파트너 서버용 인증 수단을 추가할 수 있다.
- **Cons:** 키 회전 관리를 별도로 만들어야 한다.
- **Rejected because:** 키 회전 관리 기능을 따로 구축해야 하는 부담 때문에 접었다.

## Consequences

### Positive

- 파트너사 서버가 쿠키 처리 없이 API를 호출할 수 있다.
- 파트너용 API 키 발급·회전 관리 체계를 별도로 만들지 않아도 된다.

### Negative

- 기존 세션 기반 인증 코드(`src/auth.js`)와 이를 쓰는 라우트를 JWT 발급·검증 방식으로 다시 작성해야 한다.

### Risks

- 현재 `src/auth.js`가 여전히 `require('express-session')`을 하고 있어, 의존성 재설치 후에는 모듈을 찾지 못해 서버 기동이 실패한다. 코드 전환 전까지 이 불일치를 해소해야 한다.
- JWT는 서버 측 세션과 달리 발급된 토큰을 즉시 무효화하기 어렵고, 서명 비밀키 관리·교체 방안이 필요하다.

## Implementation

- [x] `package.json`에서 express-session 제거, jsonwebtoken ^9.0.2 추가
- [ ] `src/auth.js`를 jsonwebtoken 기반 JWT 검증 미들웨어로 교체 (express-session 참조 제거)
- [ ] 파트너 서버 JWT 인증 흐름 테스트
- [ ] 인증 실패(토큰 누락·만료·서명 오류) 모니터링
- [ ] `SESSION_SECRET` 등 환경변수·파트너 연동 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `git checkout HEAD -- package.json`으로 express-session 의존성을 복원하고 `src/auth.js`를 세션 미들웨어로 되돌린다(현재 `src/auth.js`는 아직 세션 방식이라 코드 롤백은 불필요). 파트너에 JWT 발급을 시작한 뒤라면 파트너 측 인증 방식도 되돌려야 한다.
- **Migration Cost:** Low

## References

- **Documentation:** `package.json` 의존성 변경은 미커밋 상태(기준 HEAD `2de7403` feat: 파트너 주문 조회 API)
