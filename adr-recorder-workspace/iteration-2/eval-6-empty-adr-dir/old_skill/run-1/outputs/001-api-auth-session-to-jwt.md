# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway의 API 인증을 express-session 쿠키 세션에서 jsonwebtoken 기반 JWT 인증으로 바꾼다.
- **Scope:** partner-gateway / API 인증 (`src/auth.js`)
- **Decision Source:** Human

---

## Context

### Problem

파트너사 서버들이 API에 붙기 시작했는데, 쿠키 기반 세션 인증은 서버 간 호출에서 다루기 번거롭다. 파트너 서버가 세션 쿠키를 받아 보관하고 매 요청마다 다시 보내야 해서 연동 부담이 크다.

### Constraints

- API를 호출하는 쪽은 브라우저가 아니라 파트너사 서버다.
- 파트너 인증 때문에 키 회전 관리 같은 별도 운영 체계를 새로 만들지 않는다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 서버에 세션 상태를 두지 않고, 요청에 실려 오는 JWT를 서버가 검증하는 방식으로 인증한다.
- **Implementation:** `package.json` 의존성은 이미 교체했다. 다만 `src/auth.js`는 아직 `require('express-session')`로 세션 미들웨어를 내보내고 있어서 코드 전환은 끝나지 않았다.

## Rationale

1. 파트너사 서버 간 연동에서는 쿠키 기반 세션이 번거롭다. JWT는 쿠키 없이 요청마다 실어 보낼 수 있다.
2. 세션을 유지하면서 파트너용 API 키를 따로 발급하려면 키 회전 관리를 별도로 만들어야 한다. JWT를 쓰면 그런 체계를 새로 만들지 않고 인증 방식을 하나로 가져갈 수 있다.

## Alternatives

### express-session 유지 + 파트너용 API 키 발급

- **Pros:** 기존 세션 인증은 그대로 두고 파트너용 인증 경로만 더하면 된다.
- **Cons:** 파트너 API 키의 발급·회전 관리 체계를 따로 만들어야 한다. 인증 방식도 세션과 API 키 두 가지로 나뉜다.
- **Rejected because:** 키 회전 관리를 따로 만들어야 해서.
- **Recheck if:** 키 발급·회전을 직접 구현하지 않아도 되는 수단이 생길 때 (예: 게이트웨이나 시크릿 매니저가 API 키 관리 기능을 제공하는 경우).

## Consequences

### Positive

- 파트너 서버는 쿠키를 저장하고 다시 보낼 필요 없이 토큰만 실어서 API를 호출하면 된다.
- 서버에 세션 상태를 두지 않으므로 express-session 의존성이 빠진다.

### Negative

- 발급한 JWT는 만료 전에 서버에서 바로 무효화하기 어렵다. 필요하다면 만료 시간을 짧게 잡거나 차단 목록을 따로 둬야 한다.
- 기존에 쿠키 세션으로 붙던 호출자가 있다면 그쪽도 인증 방식을 바꿔야 한다.

### Risks

- JWT 서명 키에도 교체(회전) 절차가 필요하다. API 키 안을 기각한 이유와 같은 종류의 운영 부담이 서명 키 수준에서 남는다.
- 지금은 `src/auth.js`가 이미 뺀 express-session을 require하고 있다. 이 상태로 클린 설치하면 모듈을 찾지 못해 서버가 뜨지 않는다.

## Implementation

- [x] `package.json`: jsonwebtoken 추가, express-session 제거
- [ ] 구현 작업: `src/auth.js`를 JWT 검증 미들웨어로 교체해 express-session 참조를 없애고, 파트너 서버용 토큰 발급 경로를 만든다.
- [ ] 테스트: 유효·만료·위조 토큰 각각의 인증 결과 검증
- [ ] 모니터링: 인증 실패(만료, 서명 불일치) 추이 확인
- [ ] 문서/설정 업데이트: `SESSION_SECRET` 환경변수를 JWT 서명 키 설정으로 바꾸고, 파트너 연동 가이드를 갱신한다.

## Reversibility

- **Reversible:** Partial
- **Rollback:** express-session 의존성과 세션 미들웨어를 되돌린다. 파트너 서버가 이미 JWT로 연동했다면 그쪽 호출 방식도 같이 되돌려야 한다.
- **Migration Cost:** Medium

## Review Trigger

- 키 발급·회전을 직접 구현하지 않아도 되는 수단이 생길 때 → "express-session 유지 + 파트너용 API 키 발급" 안을 다시 검토한다.

## References

- **Documentation:** `package.json` 의존성 변경 (미커밋, HEAD `a904a39` 기준), `src/auth.js`
