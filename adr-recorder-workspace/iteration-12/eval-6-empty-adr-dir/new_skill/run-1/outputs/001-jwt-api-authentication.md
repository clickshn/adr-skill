# ADR-001: API 인증을 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** partner-gateway의 API 인증을 express-session 기반 쿠키 세션에서 JWT(jsonwebtoken)로 교체한다.
- **Scope:** partner-gateway (API 인증 계층)
- **Decision Source:** Human

---

## Context

### Problem

파트너사 서버들이 partner-gateway API에 연동되기 시작하면서 기존의 express-session 쿠키 세션 방식이 번거로워졌다. 쿠키 세션은 브라우저 클라이언트를 전제로 한 방식이라, 서버 대 서버로 붙는 파트너사 연동에는 잘 맞지 않는다.

### Constraints

- 인증 대상이 브라우저 사용자만이 아니라 외부 파트너사 서버를 포함한다.
- 파트너사별 자격 증명 관리에 별도의 운영 체계를 새로 만드는 부담은 피하고 싶다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (package.json에 추가, express-session ^1.18.0 제거)
- **Architecture:** 서버 측 세션 저장소에 의존하는 상태 기반 쿠키 인증을 버리고, 요청마다 토큰을 검증하는 무상태(stateless) 토큰 인증으로 전환한다.
- **Implementation:** 현재 package.json 의존성만 교체된 상태이며, 인증 미들웨어인 `src/auth.js`는 아직 express-session을 사용하고 있어 JWT 검증 미들웨어로 교체가 필요하다.

## Rationale

1. 파트너사 서버들이 연동되면서 쿠키 기반 인증의 운영이 번거로워졌고, 서버 대 서버 호출에는 헤더로 실어 보내는 토큰 방식이 더 자연스럽다.
2. JWT는 무상태 검증이 가능해 서버 측 세션 저장소와 그에 딸린 운영 부담이 없다.
3. 대안이었던 파트너용 API 키 발급과 달리, 별도의 키 회전 관리 체계를 새로 구축하지 않아도 된다.

## Alternatives

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 express-session 기반 인증을 그대로 두고, 파트너사 연동만 별도 자격 증명으로 처리할 수 있다.
- **Cons:** 파트너사 API 키의 수명 주기를 관리할 체계가 추가로 필요하다.
- **Rejected because:** 키 회전 관리를 별도로 만들어야 해서 접었다.

## Consequences

### Positive

- 파트너사 서버가 쿠키 처리 없이 헤더 토큰만으로 인증할 수 있다.
- 서버 측 세션 저장소가 사라져 인증 계층이 무상태가 된다.

### Negative

- 발급된 JWT는 만료 전에 서버에서 즉시 무효화하기 어렵다. 세션 방식에서 가능했던 즉시 로그아웃/차단이 그대로 유지되지 않는다.
- 기존 쿠키 세션을 쓰던 클라이언트는 토큰 방식으로 함께 전환해야 한다.

### Risks

- 서명 키(secret) 유출 시 영향 범위가 세션 방식보다 크다. 키 보관과 교체 절차가 필요하다.
- `src/auth.js`가 아직 express-session을 require하고 있어, 의존성만 제거된 현재 상태에서는 모듈 해석이 실패한다. 코드 교체 전까지 미완성 상태다.

## Implementation

- [ ] `src/auth.js`를 express-session 미들웨어에서 JWT 검증 미들웨어로 교체
- [ ] 토큰 발급 경로와 만료 정책 결정, 서명 키 환경변수(`SESSION_SECRET` 대체) 정리
- [ ] 인증 성공/실패 및 만료 토큰 처리에 대한 테스트
- [ ] 인증 실패율 모니터링
- [ ] 파트너사 연동 문서에 토큰 사용법 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json에서 jsonwebtoken을 제거하고 express-session ^1.18.0을 되돌린 뒤 `src/auth.js`를 세션 미들웨어로 복원한다. 현재 작업 트리 변경은 커밋 전이므로 HEAD(`2a29f15`) 기준으로 되돌리면 된다. 세션은 영속 데이터가 아니어서 마이그레이션할 저장소가 없다.
- **Migration Cost:** Low
