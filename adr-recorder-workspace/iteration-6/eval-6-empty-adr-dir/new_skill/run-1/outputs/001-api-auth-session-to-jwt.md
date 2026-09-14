# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway API 인증 방식을 express-session 기반 쿠키 세션에서 jsonwebtoken 기반 JWT로 교체한다.
- **Scope:** partner-gateway / API 인증 미들웨어 (src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

- 파트너사 서버들이 API에 붙기 시작하면서, 서버 간(server-to-server) 호출에 쿠키 기반 세션 인증을 쓰는 것이 번거로워졌다.
- 현재 인증은 src/auth.js의 express-session 미들웨어(SESSION_SECRET, resave: false, saveUninitialized: false)로 구성되어 있으며, 세션 store가 따로 지정되어 있지 않아 기본 MemoryStore를 쓰는 상태다.

### Constraints

- 파트너사 서버가 쿠키 처리 없이 호출할 수 있는 인증 방식이어야 한다.
- 파트너별 키 회전 관리 같은 별도 관리 기능을 새로 만들지 않는다.
- 기존 Express 4(express ^4.19.2) 기반 구조를 유지한다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 쿠키 기반 서버 세션 대신, 요청마다 전달되는 JWT를 서버가 서명 검증하는 토큰 기반 인증
- **Implementation:** package.json에서 express-session을 빼고 jsonwebtoken을 추가함(작업 트리 변경, 미커밋). src/auth.js의 세션 미들웨어를 JWT 검증 미들웨어로 교체해야 함

## Rationale

1. 파트너사 서버 연동에서 쿠키 기반 세션이 번거로운데, JWT는 쿠키 없이 요청 단위로 토큰을 전달하므로 서버 간 호출에 맞다.
2. 세션을 유지하면서 파트너용 API 키를 따로 발급하는 방식은 키 회전 관리를 별도로 만들어야 하므로, 인증 방식을 JWT 하나로 바꾸는 쪽을 택했다.

## Alternatives

### express-session 유지 + 파트너용 API 키 발급

- **Pros:** 기존 세션 인증을 그대로 두고 파트너 호출 경로만 추가하면 된다.
- **Cons:** 파트너별 API 키의 발급·회전 관리를 별도로 구현해야 한다.
- **Rejected because:** 키 회전 관리를 따로 만들어야 해서 접었다.
- **Recheck if:** 키 회전 관리를 직접 만들지 않고 해결할 수 있는 수단이 생기는 경우

## Consequences

### Positive

- 파트너사 서버가 쿠키 처리 없이 토큰만으로 API를 호출할 수 있다.
- 서버 측 세션 상태(현재 기본 MemoryStore)에 의존하지 않게 된다.

### Negative

- 기존 쿠키 세션을 쓰던 클라이언트는 토큰 기반 인증으로 옮겨야 한다.
- 토큰 발급 흐름(누가, 어떤 절차로 파트너에게 JWT를 발급하는지)을 새로 정의해야 한다.

### Risks

- 현재 src/auth.js가 여전히 `require('express-session')`을 하고 있어, package.json 기준으로 의존성을 다시 설치하면 모듈 로드 실패로 서버가 뜨지 않는다.
- JWT는 서버 세션처럼 즉시 무효화하기 어려워, 만료 시간과 폐기 방안을 정하지 않으면 유출된 토큰이 만료 전까지 유효하다.
- JWT 서명 키도 교체 절차는 필요하다(파트너별 키가 아닌 서버 측 서명 키 기준).

## Implementation

- [ ] src/auth.js의 express-session 미들웨어를 jsonwebtoken 기반 JWT 검증 미들웨어로 교체
- [ ] 파트너용 토큰 발급 흐름과 토큰 만료 시간 정의
- [ ] 유효/만료/위조 토큰에 대한 인증 미들웨어 테스트
- [ ] 인증 실패(401) 발생률 모니터링
- [ ] SESSION_SECRET 대신 JWT 서명 키 환경변수 설정 및 파트너 연동 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json을 HEAD 버전(express-session ^1.18.0, jsonwebtoken 없음)으로 되돌리고 src/auth.js의 세션 미들웨어를 유지·복원한다. 파트너사가 JWT로 연동한 뒤에는 파트너 측 호출 방식도 함께 되돌려야 한다.
- **Migration Cost:** Low

## Review Trigger

- 키 회전 관리를 직접 만들지 않고 해결할 수 있는 수단이 생기면, 세션 유지 + 파트너용 API 키 방식을 다시 검토한다.

## References

- **Documentation:** package.json (작업 트리 변경, 미커밋), src/auth.js, 기준 커밋 2054636 (express-session 도입)
