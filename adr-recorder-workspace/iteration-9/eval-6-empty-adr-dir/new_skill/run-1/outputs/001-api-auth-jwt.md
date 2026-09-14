# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** API 인증 방식을 express-session 기반 쿠키 세션에서 jsonwebtoken 기반 JWT로 전환한다.
- **Scope:** partner-gateway / API 인증 (`src/auth.js`)
- **Decision Source:** Human

---

## Context

### Problem

파트너사 서버들이 API에 붙기 시작하면서, 브라우저 전제의 쿠키 기반 세션 인증(express-session)을 서버 간 호출에 적용하는 것이 번거로워졌다.

### Constraints

- Express 4(`express ^4.19.2`) 기반 partner-gateway 서비스다.
- 파트너용 키 회전 관리 같은 별도 관리 체계를 새로 만들지 않는 범위에서 해결한다.

## Decision

### Selected

- **Technology:** jsonwebtoken `^9.0.2` (express-session `^1.18.0` 제거)
- **Architecture:** 서버 측 세션 저장소와 쿠키에 의존하는 세션 인증 대신, 요청마다 토큰을 검증하는 무상태 토큰 인증
- **Implementation:** `package.json` 의존성 교체 완료. 인증 미들웨어 `src/auth.js`는 아직 express-session 기반이다.

## Rationale

1. 파트너사 서버가 쿠키 처리 없이 토큰만으로 API를 호출할 수 있어, 쿠키 기반보다 서버 간 연동이 단순하다.
2. 세션을 유지하면서 파트너용 API 키를 따로 발급하는 방식과 달리, 키 회전 관리를 별도로 만들 필요가 없다.

## Alternatives

### 현행 유지 (express-session 쿠키 세션)

- **Pros:** 기존 구현(`src/auth.js`)을 그대로 쓸 수 있다.
- **Cons:** 파트너사 서버 연동 시 쿠키 기반 인증이 번거롭다.
- **Rejected because:** 파트너사 서버들이 붙으면서 쿠키 기반 인증이 번거로워졌다.

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 세션 인증 구조를 유지할 수 있다.
- **Cons:** 파트너용 API 키의 회전 관리를 따로 만들어야 한다.
- **Rejected because:** 키 회전 관리를 별도로 구축해야 해서 접었다.

## Consequences

### Positive

- 파트너사 서버가 쿠키·세션 없이 토큰만으로 인증할 수 있다.
- 서버 측 세션 상태가 없어져 세션 저장소를 관리하지 않아도 된다.

### Negative

- 발급된 토큰은 만료 전까지 유효하므로, 서버 측에서 개별 토큰을 즉시 무효화하기 어렵다.
- 토큰 발급·만료·서명 비밀키 관리 로직을 새로 구현해야 한다.

### Risks

- `src/auth.js`가 여전히 `require('express-session')`을 호출하는데 의존성은 이미 제거되어, JWT 미들웨어로 교체하기 전에는 새로 설치한 환경에서 모듈 로드 오류가 난다.
- JWT 서명 비밀키도 유출·교체 시 회전이 필요하므로, 키 회전 부담이 완전히 사라지는 것은 아니다(파트너별 키 관리 → 서명 키 관리로 축소).

## Implementation

- [x] `package.json`: express-session 제거, jsonwebtoken 추가
- [ ] 구현 작업: `src/auth.js`를 JWT 검증 미들웨어로 교체, 파트너용 토큰 발급 경로 마련
- [ ] 테스트: 유효/만료/위조 토큰 인증 테스트
- [ ] 모니터링: 토큰 검증 실패(401) 추이 확인
- [ ] 문서/설정 업데이트: `SESSION_SECRET`을 JWT 서명 키 설정으로 대체, 파트너 연동 가이드 갱신

## Reversibility

- **Reversible:** Yes
- **Rollback:** `git checkout HEAD -- package.json`으로 express-session 의존성을 복원한다. HEAD의 `src/auth.js`는 express-session 기반 그대로라 추가 코드 변경 없이 되돌아간다.
- **Migration Cost:** Low (파트너사가 JWT로 연동한 뒤에는 파트너 측 변경이 필요해 비용이 커진다)

## References

- **Documentation:** `package.json` 의존성 변경(작업 트리, 미커밋 / 기준 커밋 `2de7403`)
