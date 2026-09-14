# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway의 API 인증 방식을 express-session 기반 쿠키 세션에서 jsonwebtoken 기반 JWT로 교체한다.
- **Scope:** partner-gateway / API 인증 (`src/auth.js`, `package.json`)
- **Decision Source:** Human

---

## Context

### Problem

partner-gateway는 지금까지 express-session으로 쿠키 기반 세션 인증을 해 왔다(`src/auth.js`, `SESSION_SECRET` 사용). 파트너 주문 조회 API(커밋 abe4c7c)가 추가되면서 브라우저가 아닌 파트너사 서버들이 API를 직접 호출하게 되었고, 서버 간 호출에서 쿠키를 받아 저장하고 다시 보내야 하는 쿠키 기반 인증이 번거로워졌다.

### Constraints

- 인증 주체는 브라우저가 아니라 파트너사 서버이며, 이런 서버 간 호출은 쿠키를 다루기에 적합하지 않다.
- 파트너 인증을 위해 키 회전 같은 별도 자격증명 관리 체계를 새로 만들지 않아야 한다.
- 스택은 Express 4(`express ^4.19.2`)를 유지한다.

## Decision

### Selected

- **Technology:** jsonwebtoken `^9.0.2` (express-session `^1.18.0` 제거)
- **Architecture:** 서버 측 세션 저장소 없이 요청마다 JWT를 검증하는 stateless 인증
- **Implementation:** `package.json` 의존성 교체는 완료했다. 다만 `src/auth.js`는 아직 `require('express-session')`로 세션 미들웨어를 export하고 있어 JWT 검증 미들웨어로 다시 작성해야 한다.

## Rationale

1. 파트너사 서버가 붙은 뒤로는 쿠키 기반 세션 인증을 운영하기가 번거롭다. 토큰 방식이면 서버 간 호출에서 쿠키 없이 요청마다 토큰만 보내면 된다.
2. 세션을 유지하면서 파트너용 API 키를 따로 발급하는 방식보다, 키 회전 관리를 별도로 만들 필요가 없는 쪽을 택했다.

## Alternatives

### express-session 유지 + 파트너용 API 키 발급

- **Pros:** 기존 쿠키 세션 인증을 그대로 두고 파트너용 인증 경로만 추가하면 된다.
- **Cons:** 파트너별 API 키의 회전 관리를 별도로 만들어야 한다.
- **Rejected because:** 키 회전 관리를 따로 만들어야 해서 접었다.
- **Recheck if:** API 키 발급·회전 관리를 별도 구현 없이 제공받을 수 있게 되는 경우(예: 키 관리 기능을 갖춘 게이트웨이나 시크릿 관리 도구를 도입하는 경우)

## Consequences

### Positive

- 파트너사 서버가 쿠키 없이 토큰만으로 API를 호출할 수 있다.
- 서버 측 세션 저장이 필요 없어진다.

### Negative

- 인증 관련 코드(`src/auth.js`)를 다시 작성해야 한다.
- 세션과 달리 발급한 토큰을 서버에서 곧바로 무효화하기 어렵다. 만료 시간 설계가 필요하다.

### Risks

- 현재 `package.json`에서는 express-session이 빠졌지만 `src/auth.js`는 여전히 `require('express-session')`를 호출한다. 이 상태로 의존성을 새로 설치하고 실행하면 모듈을 찾지 못해 서버 기동이 실패한다.
- JWT 서명 비밀키가 유출되면 토큰을 위조할 수 있다. 서명키 교체 절차가 필요할 수 있다.

## Implementation

- [ ] `src/auth.js`를 express-session 미들웨어에서 jsonwebtoken 기반 JWT 검증 미들웨어로 교체
- [ ] 파트너 토큰 발급 방식과 만료 정책 정의
- [ ] 테스트: 유효/만료/위조 토큰에 대한 인증 동작 검증
- [ ] 모니터링: 인증 실패(401) 비율 추적
- [ ] 문서/설정 업데이트: `SESSION_SECRET` 대신 JWT 서명키용 환경변수로 교체, 파트너 연동 가이드 갱신

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`에서 `jsonwebtoken`을 빼고 `express-session ^1.18.0`을 복원한다(`git checkout HEAD -- package.json`). 현재 `src/auth.js`는 아직 세션 방식이라 코드 롤백은 필요 없다. 파트너가 JWT로 연동한 뒤에는 파트너 측 인증 방식도 되돌려야 하므로 비용이 커진다.
- **Migration Cost:** Low

## Review Trigger

- API 키 발급·회전 관리를 별도 구현 없이 제공받을 수 있게 되는 경우(예: 키 관리 기능을 갖춘 게이트웨이나 시크릿 관리 도구를 도입하는 경우)

## References

- **Documentation:** 기준 커밋 abe4c7c(feat: 파트너 주문 조회 API), 변경 파일 `package.json`(미커밋), 관련 코드 `src/auth.js`
