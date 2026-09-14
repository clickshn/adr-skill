# ADR-001: API 인증을 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** partner-gateway의 API 인증을 express-session 기반 쿠키 세션에서 JWT로 교체한다.
- **Scope:** partner-gateway / 인증 모듈(src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

파트너사 서버들이 partner-gateway에 연동되기 시작하면서 쿠키 기반 세션 인증이 번거로워졌다.
쿠키 세션은 브라우저 클라이언트를 전제로 한 방식이라, 서버 대 서버로 붙는 파트너사 연동에는
잘 맞지 않는다.

### Constraints

- 현재 인증은 `src/auth.js`의 `express-session` 미들웨어 하나로 구성되어 있고, secret은
  `SESSION_SECRET` 환경변수에서 읽는다.
- `package.json`에서 `express-session`을 제거하고 `jsonwebtoken ^9.0.2`를 추가한 상태이나,
  `src/auth.js`는 아직 `express-session`을 그대로 사용하고 있어 현재 작업 트리는 의존성과
  코드가 어긋나 있다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 서버 측 세션 저장소 없이 토큰 자체에 인증 정보를 담는 무상태(stateless) 인증.
  파트너사 서버는 발급받은 JWT를 요청 헤더로 전달한다.
- **Implementation:** `src/auth.js`의 express-session 미들웨어를 JWT 검증 미들웨어로 교체하고,
  `SESSION_SECRET` 기반 설정을 JWT 서명 키 설정으로 대체한다.

## Rationale

1. 파트너사 서버 연동이 늘어나면서 쿠키 기반 인증의 운영 부담이 실제로 발생했다.
2. JWT는 서버 대 서버 호출에서 헤더로 자격 증명을 전달하는 방식이라 쿠키 저장·전달 문제가 없다.
3. 대안이었던 API 키 방식과 달리, 키 회전 관리 체계를 새로 만들지 않아도 된다.

## Alternatives

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 express-session 구현을 그대로 두고 파트너사 연동만 별도 인증 경로로 수용할 수 있다.
- **Cons:** 파트너별 API 키의 회전 관리 체계를 별도로 구축해야 한다.
- **Rejected because:** 키 회전 관리를 따로 만들어야 하는 부담이 커서 접었다.

## Consequences

### Positive

- 파트너사 서버가 쿠키 처리 없이 헤더만으로 인증할 수 있다.
- 서버 측 세션 저장소에 대한 의존이 사라져 인증이 무상태가 된다.

### Negative

- 발급된 토큰은 만료 전까지 서버에서 즉시 무효화하기 어렵다. 세션 삭제로 즉시 로그아웃시키던
  동작은 그대로 옮길 수 없다.
- 기존 쿠키 세션을 쓰던 클라이언트가 있다면 전환 작업이 필요하다.

### Risks

- `package.json`에서 이미 express-session이 빠졌지만 `src/auth.js`는 아직 이를 require하므로,
  이 상태로 설치·기동하면 모듈을 찾지 못해 실패한다. 코드 교체 전까지 배포하면 안 된다.
- JWT 서명 키 관리(주입 경로, 유출 시 대응)를 `SESSION_SECRET` 수준 이상으로 정의해야 한다.

## Implementation

- [ ] `src/auth.js`를 JWT 검증 미들웨어로 교체하고 서명 키 설정 경로 확정
- [ ] 토큰 발급 경로 및 만료 정책 정의
- [ ] 인증 성공/실패 및 만료 토큰에 대한 테스트
- [ ] 인증 실패율·토큰 만료 관련 모니터링
- [ ] 파트너사 연동 문서와 환경변수 설정 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`의 의존성 변경을 되돌려 express-session을 복원한다. `src/auth.js`는
  아직 수정되지 않았으므로 현재 시점에서는 코드 롤백이 필요 없다. 세션 설정 원본은 커밋
  `2054636`에 있다.
- **Migration Cost:** Low

## References

- **Documentation:** `package.json`(작업 트리 변경, 미커밋), `src/auth.js`, 기준 커밋 `2054636`
