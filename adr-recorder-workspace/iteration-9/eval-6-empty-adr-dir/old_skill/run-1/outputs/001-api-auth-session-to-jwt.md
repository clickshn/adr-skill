# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway의 API 인증 방식을 express-session 기반 쿠키 세션에서 jsonwebtoken 기반 JWT로 바꾼다.
- **Scope:** partner-gateway / API 인증 (src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

partner-gateway는 현재 express-session 쿠키 세션으로 API를 인증한다(src/auth.js). 파트너사 서버들이 API에 붙기 시작하면서(최근 커밋 2de7403 "파트너 주문 조회 API") 쿠키 기반 인증을 쓰기가 번거로워졌다.

### Constraints

- 호출 주체가 브라우저 사용자가 아니라 파트너사 서버이므로, 서버 간 호출에서 쓰기 쉬운 인증 방식이어야 한다.
- 기존 Express 4(`express ^4.19.2`) 기반 구조는 유지한다.
- 인증 수단 관리를 위한 별도 시스템(예: 키 회전 관리)을 새로 만드는 것은 피하고 싶다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 서버 측 세션 상태를 두는 쿠키 세션 대신, 요청마다 토큰을 검증하는 stateless JWT 인증으로 바꾼다.
- **Implementation:** package.json 의존성 교체는 끝났다. src/auth.js의 express-session 미들웨어를 JWT 검증 미들웨어로 바꾸는 작업이 남아 있다.

## Rationale

1. 파트너사 서버가 쿠키를 주고받지 않고 토큰만 실어 호출할 수 있어서, 쿠키 기반 방식의 번거로움이 사라진다.
2. 세션을 유지하면서 파트너용 API 키를 따로 발급하는 방식과 달리, 키 회전 관리 기능을 새로 만들 필요가 없다.

## Alternatives

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 express-session 쿠키 세션 인증을 그대로 둘 수 있다.
- **Cons:** 파트너용 API 키의 회전을 관리하는 기능을 따로 만들어야 한다.
- **Rejected because:** 키 회전 관리를 별도로 구현해야 하는 부담 때문에 접었다.
- **Recheck if:** 키 회전 관리를 별도 구현 없이 해결할 수단이 생기면(예: 이미 갖춰진 키 관리 기능이나 외부 서비스를 도입하게 되는 경우)

## Consequences

### Positive

- 파트너사 서버가 쿠키 처리 없이 API를 호출할 수 있다.
- 서버 측 세션 저장 상태가 필요 없어진다.

### Negative

- 서버에 세션이 없으므로 발급된 토큰을 만료 전에 개별 폐기하기가 쿠키 세션보다 어렵다.
- 세션 방식에 맞춰 짜인 기존 인증 코드(src/auth.js)를 다시 작성해야 한다.

### Risks

- src/auth.js가 아직 `require('express-session')`을 호출한다. package.json에서 express-session을 뺐기 때문에, 코드를 바꾸기 전에 의존성을 새로 설치하면 앱이 시작될 때 모듈 로드에 실패한다.
- JWT 서명 비밀키(현재 `SESSION_SECRET` 환경 변수를 쓰는 구조)가 유출되면 모든 토큰을 위조할 수 있다. 서명 키 교체 절차도 필요해질 수 있다.

## Implementation

- [ ] src/auth.js의 express-session 미들웨어를 jsonwebtoken 기반 JWT 검증 미들웨어로 교체
- [ ] 파트너 주문 조회 API 등 기존 인증 경로가 JWT로 동작하는지 테스트
- [ ] 토큰 검증 실패·만료 건수 모니터링
- [ ] JWT 서명 키 환경 변수 설정과 파트너사 연동 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `git checkout HEAD -- package.json`으로 express-session 의존성을 되돌린다. src/auth.js는 아직 세션 방식이라 코드는 되돌릴 게 없다. 다만 파트너사들이 JWT로 연동한 뒤에 되돌리면 각 파트너가 연동 방식을 다시 바꿔야 한다.
- **Migration Cost:** Low

## Review Trigger

- 키 회전 관리를 별도 구현 없이 해결할 수단이 생기면(예: 이미 갖춰진 키 관리 기능이나 외부 서비스를 도입하게 되는 경우) "세션 방식 유지 + 파트너용 API 키 발급" 대안을 다시 검토한다.

## References

- **Documentation:** 기준 커밋 2de7403 (feat: 파트너 주문 조회 API), 변경 파일 package.json, 영향 파일 src/auth.js
