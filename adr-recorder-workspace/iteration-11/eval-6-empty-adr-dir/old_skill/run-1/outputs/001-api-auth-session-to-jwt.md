# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** partner-gateway API 인증을 express-session 쿠키 세션 대신 jsonwebtoken 기반 JWT로 처리한다.
- **Scope:** partner-gateway / API 인증 (`src/auth.js`)
- **Decision Source:** Human

---

## Context

### Problem

파트너사 서버들이 API에 붙기 시작하면서(최근 커밋 `1f85596 feat: 파트너 주문 조회 API`) 기존 express-session 쿠키 세션 기반 인증이 번거로워졌다.

### Constraints

- API를 호출하는 주체에 파트너사 서버가 포함된다.
- 파트너용 API 키를 도입하려면 키 회전 관리를 따로 만들어야 한다.
- 현재 인증 미들웨어(`src/auth.js`)는 express-session을 `SESSION_SECRET` 환경변수로 구성하고 있다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 쿠키 세션 대신 요청에 담긴 JWT를 검증하는 토큰 기반 인증
- **Implementation:** `package.json` 의존성 교체는 반영됨(미커밋). `src/auth.js`는 아직 express-session 기반이라 JWT 검증 미들웨어로 교체가 필요하다.

## Rationale

1. 파트너사 서버들이 붙으면서 쿠키 기반 세션 인증이 번거로워졌다.
2. 세션 방식을 유지하면서 파트너용 API 키를 발급하는 방안은 키 회전 관리를 따로 만들어야 해서 접었다.

## Alternatives

### 현행 유지: express-session 쿠키 세션

- **Pros:** 이미 `src/auth.js`에 구성되어 있어 추가 작업이 없다.
- **Cons:** 파트너사 서버 연동에서 쿠키 기반이 번거롭다.
- **Rejected because:** 파트너사 서버들이 붙으면서 쿠키 기반이 번거로워졌다.

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 세션 인증을 그대로 두고 파트너 호출만 API 키로 분리할 수 있다.
- **Cons:** 키 회전 관리를 별도로 만들어야 한다.
- **Rejected because:** 키 회전 관리를 따로 만들어야 해서 접었다.

## Consequences

### Positive

- 파트너사 서버가 쿠키 없이 토큰으로 API를 호출할 수 있다.
- express-session 의존성이 제거된다.

### Negative

- 발급된 JWT는 만료 전까지 서버에서 즉시 무효화하기 어렵다(세션 삭제로 끊던 방식과 다름).
- JWT 서명 키 관리가 새로 필요하다.

### Risks

- `src/auth.js`가 여전히 `require('express-session')`을 하고 있어, 의존성 제거 상태로 설치·기동하면 모듈을 찾지 못해 서버가 시작되지 않는다. 인증 코드 교체가 의존성 변경과 함께 반영되어야 한다.
- 토큰 만료·폐기 정책이 정해지지 않으면 유출된 토큰이 오래 유효할 수 있다.

## Implementation

- [ ] `src/auth.js`를 express-session에서 jsonwebtoken 기반 JWT 검증 미들웨어로 교체
- [ ] 파트너용 토큰 발급 방식과 만료 정책 정의
- [ ] JWT 서명 키 환경변수 설정(`SESSION_SECRET` 대체)
- [ ] 테스트: 정상 토큰, 만료 토큰, 위조 토큰, 토큰 누락
- [ ] 모니터링: 인증 실패(401) 추이
- [ ] 문서/설정 업데이트: 파트너 연동 가이드에 인증 방식 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`에서 jsonwebtoken을 빼고 `express-session ^1.18.0`을 복원한다(`git checkout HEAD -- package.json`). 현재 `src/auth.js`는 아직 세션 방식이라 코드 롤백은 필요 없다. 파트너가 JWT로 연동한 뒤에는 파트너 측 인증 방식도 함께 되돌려야 해 비용이 커진다.
- **Migration Cost:** Low

## References

- **Documentation:** 의존성 변경 `package.json`(미커밋, HEAD `1f85596` 기준), 인증 미들웨어 `src/auth.js`
