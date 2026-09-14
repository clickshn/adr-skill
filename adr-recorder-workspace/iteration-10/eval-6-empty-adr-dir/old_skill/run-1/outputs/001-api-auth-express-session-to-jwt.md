# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway의 API 인증 방식을 express-session 기반 쿠키 세션에서 jsonwebtoken 기반 JWT로 바꾼다.
- **Scope:** partner-gateway / API 인증 계층 (src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

partner-gateway는 express-session 쿠키 세션으로 API 요청을 인증한다(src/auth.js). 파트너사 서버들이 API에 붙기 시작하면서, 브라우저가 아닌 서버 간 호출에서 쿠키 기반 세션을 유지·전달하는 방식이 번거로워졌다.

### Constraints

- 파트너사 서버가 서버 간 호출로 API에 붙어야 한다.
- 파트너용 자격 증명을 위한 키 회전 관리 기능을 따로 만들고 싶지 않다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 서버 측 세션 저장소와 쿠키 대신, 요청마다 전달되는 서명된 JWT로 인증한다.
- **Implementation:** package.json에서 express-session을 빼고 jsonwebtoken을 추가했다(미커밋 변경). src/auth.js는 아직 express-session 미들웨어를 그대로 쓰고 있어 JWT 검증 미들웨어로 바꿔야 한다.

## Rationale

1. 파트너사 서버 연동에서 쿠키 기반 세션보다 요청에 토큰을 실어 보내는 방식이 다루기 쉽다.
2. 세션 방식을 유지하면서 파트너용 API 키를 발급하는 방안은 키 회전 관리를 따로 만들어야 해서, JWT로 한 번에 전환하는 쪽을 택했다.

## Alternatives

### express-session 쿠키 세션 유지 (현행 유지)

- **Pros:** 이미 적용된 방식이라 추가 작업이 없다.
- **Cons:** 파트너사 서버가 붙는 서버 간 호출에서 쿠키 기반 처리가 번거롭다.
- **Rejected because:** 파트너사 서버 연동에 쿠키 기반 방식이 번거롭다.

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 express-session 인증을 그대로 두고 파트너 호출만 API 키로 따로 처리할 수 있다.
- **Cons:** API 키의 회전 관리를 별도로 만들어야 한다.
- **Rejected because:** 키 회전 관리를 따로 만들어야 하는 부담 때문에 접었다.

## Consequences

### Positive

- 파트너사 서버가 쿠키를 다루지 않고 토큰만으로 API를 호출할 수 있다.
- 서버 측 세션 저장소가 필요 없어진다.

### Negative

- 인증 방식이 바뀌므로 기존 쿠키 세션에 의존하던 클라이언트는 토큰 기반으로 옮겨야 한다.
- JWT는 서버에 상태가 없어, 발급된 토큰을 만료 전에 개별적으로 무효화하려면 별도 장치가 필요하다.

### Risks

- src/auth.js가 여전히 `require('express-session')`을 하고 있어, 의존성을 제거한 현재 상태로 설치·실행하면 모듈 로드에 실패한다.
- JWT 서명 비밀 키(현재 SESSION_SECRET 환경 변수를 쓰는 자리)의 보관·교체 방식은 아직 정해지지 않았다.

## Implementation

- [ ] src/auth.js를 express-session 미들웨어에서 jsonwebtoken 기반 JWT 검증 미들웨어로 교체
- [ ] 파트너 토큰 발급 흐름 구현
- [ ] 인증 성공/실패(만료·서명 오류) 테스트
- [ ] 인증 실패율 모니터링
- [ ] SESSION_SECRET 대신 쓸 JWT 서명 키 환경 변수 설정 및 파트너 연동 문서 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json에 express-session ^1.18.0을 되돌리고 jsonwebtoken을 제거한 뒤, src/auth.js를 커밋 2de7403 시점의 세션 미들웨어로 복원한다. 파트너사가 JWT로 연동한 뒤라면 파트너 쪽 호출 방식도 함께 되돌려야 한다.
- **Migration Cost:** Medium

## References

- **Documentation:** 변경 기준 커밋 2de7403 (feat: 파트너 주문 조회 API), 변경 파일 package.json, src/auth.js
