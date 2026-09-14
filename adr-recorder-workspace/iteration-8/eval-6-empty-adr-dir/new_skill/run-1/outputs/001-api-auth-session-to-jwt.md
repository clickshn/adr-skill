# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway API 인증을 express-session 쿠키 세션에서 jsonwebtoken 기반 JWT로 바꾼다.
- **Scope:** partner-gateway / API 인증 (src/auth.js, package.json)
- **Decision Source:** Human

---

## Context

### Problem

파트너사 서버들이 API에 붙기 시작하면서, 쿠키 기반 세션 인증은 서버 간 연동에서 다루기 번거로워졌다.

### Constraints

- 서비스는 Express 4(`express ^4.19.2`) 기반이며, 인증은 `src/auth.js`의 express-session 미들웨어(`SESSION_SECRET` 환경변수 사용) 한 곳에서 구성되어 있다.
- 주 사용자는 브라우저가 아닌 파트너사 서버이다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 쿠키 기반 서버 세션 → 요청마다 토큰을 제시하는 JWT 인증
- **Implementation:** `package.json`에서 express-session을 빼고 jsonwebtoken을 추가함(작업 트리 반영, 미커밋). `src/auth.js`는 아직 express-session을 사용 중이며 JWT 방식으로 전환해야 한다.

## Rationale

1. 파트너사 서버 연동에서 쿠키 기반 세션이 번거로워, 쿠키에 의존하지 않는 토큰 방식으로 바꾼다.
2. 세션 방식을 유지하면서 파트너용 API 키를 따로 발급하는 방안은 키 회전 관리를 별도로 만들어야 해서, 인증 방식을 JWT 하나로 바꾸는 쪽을 택했다.

## Alternatives

### 현행 유지 (express-session 쿠키 세션)

- **Pros:** 이미 `src/auth.js`에 구성되어 있어 추가 작업이 없다.
- **Cons:** 파트너사 서버 연동 시 쿠키 기반 인증이 번거롭다.
- **Rejected because:** 파트너사 서버들이 붙으면서 쿠키 기반이 번거로워졌다.

### 세션 유지 + 파트너용 API 키 발급

- **Pros:** 기존 쿠키 세션을 그대로 유지할 수 있다.
- **Cons:** 파트너용 API 키의 회전(rotation) 관리를 따로 만들어야 한다.
- **Rejected because:** 키 회전 관리를 별도로 구축해야 해서 접었다.

## Consequences

### Positive

- 파트너사 서버가 쿠키 처리 없이 토큰만으로 API를 호출할 수 있다.
- 서버 측 세션 상태를 유지하지 않아도 된다.

### Negative

- 발급된 토큰은 만료 전까지 유효하므로, 세션 삭제처럼 즉시 무효화하기 어렵다.
- JWT 서명 비밀키의 보관·교체 절차가 필요하다.

### Risks

- `package.json`에서 express-session이 빠졌지만 `src/auth.js`는 여전히 `require('express-session')`을 호출한다. 이 상태로 의존성을 새로 설치해 배포하면 모듈을 찾지 못해 기동이 실패한다.

## Implementation

- [ ] `src/auth.js`를 express-session 미들웨어에서 JWT 검증 미들웨어로 교체
- [ ] 테스트: 유효/만료/위조 토큰에 대한 인증 동작 검증
- [ ] 모니터링: 인증 실패(토큰 오류) 응답 추이 확인
- [ ] 문서/설정 업데이트: `SESSION_SECRET` 대신 JWT 서명용 비밀키 환경변수 설정, 파트너사 대상 토큰 사용 안내

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`을 HEAD 상태로 되돌려(`git checkout HEAD -- package.json`) express-session을 복구한다. 현재 `src/auth.js`는 아직 세션 방식이라 코드 수정은 필요 없다. 파트너사가 JWT 연동을 시작한 뒤라면 파트너 측 인증 방식도 되돌려야 한다.
- **Migration Cost:** Low

## References

- **Documentation:** 기준 커밋 `2de7403` (feat: 파트너 주문 조회 API) / 변경 파일 `package.json`(미커밋), 영향 파일 `src/auth.js`
