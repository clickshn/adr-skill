# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway의 API 인증 방식을 express-session 기반 쿠키 세션에서 jsonwebtoken 기반 JWT로 교체한다.
- **Scope:** partner-gateway / API 인증 (src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

partner-gateway의 API 인증은 express-session 쿠키 세션(`src/auth.js`, `SESSION_SECRET` 서명)으로 구현돼 있다. 파트너 주문 조회 API(cd54b25)가 추가되면서 파트너사 서버들이 API에 직접 붙게 되었는데, 서버 간(server-to-server) 호출에서 쿠키를 받아 보관하고 다시 보내는 방식은 파트너 쪽 구현이 번거롭다.

### Constraints

- 호출 주체가 브라우저가 아닌 파트너사 서버이므로, 쿠키에 의존하지 않고 요청 헤더만으로 인증할 수 있어야 한다.
- 파트너 대상 인증 방식을 새로 만들 때 키 회전 같은 별도 관리 체계를 추가로 구축하는 부담은 피하고자 한다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 서버 측 세션 저장소에 기대는 쿠키 세션 대신, 요청마다 토큰을 담아 보내고 서명으로 검증하는 무상태 토큰 인증
- **Implementation:** `package.json`에서 express-session을 빼고 jsonwebtoken을 추가함(커밋 전). `src/auth.js`는 아직 `require('express-session')`을 쓰는 세션 미들웨어 그대로이므로 JWT 검증 미들웨어로 교체해야 한다.

## Rationale

1. 파트너사 서버가 쿠키를 다룰 필요 없이 요청 헤더에 토큰만 실어 보내면 되므로 서버 간 연동이 쉬워진다.
2. 세션을 유지한 채 파트너용 API 키를 따로 발급하는 방식과 달리, 키 회전 관리 체계를 별도로 만들지 않아도 된다.
3. 인증 방식을 하나로 통일하므로 세션과 API 키를 함께 운영하는 이중 체계를 피할 수 있다.

## Alternatives

### express-session 쿠키 세션 유지 + 파트너용 API 키 발급

- **Pros:** 기존 세션 인증 흐름을 그대로 두고 파트너 경로만 추가하면 된다.
- **Cons:** 파트너별 API 키의 발급·회전을 관리하는 기능을 따로 만들어야 하고, 세션과 API 키라는 두 가지 인증 방식을 함께 운영해야 한다.
- **Rejected because:** 키 회전 관리를 별도로 구현해야 하는 부담이 커서 접었다.
- **Recheck if:** 키 발급·회전을 대신 처리해 줄 수단(시크릿 관리 도구, API 게이트웨이 등)이 도입되어 회전 관리를 직접 만들 필요가 없어질 때

## Consequences

### Positive

- 파트너사 서버가 쿠키 없이 헤더 기반으로 인증해 연동할 수 있다.
- 서버 측 세션 상태가 필요 없어져 인증이 무상태가 된다.

### Negative

- `src/auth.js`의 세션 미들웨어를 JWT 검증 미들웨어로 새로 작성해야 하며, 기존 세션 쿠키로 인증하던 클라이언트는 토큰 방식으로 옮겨야 한다.
- 세션은 서버에서 지우면 끝나지만, JWT는 발급 후 만료 전까지 유효하므로 강제 무효화(로그아웃·권한 회수)를 따로 설계해야 한다.

### Risks

- 현재 `package.json`에서는 express-session이 빠졌지만 `src/auth.js`는 여전히 `require('express-session')`을 호출한다. 이 상태로 의존성을 새로 설치해 배포하면 `Cannot find module 'express-session'` 오류로 서버가 뜨지 않는다.
- JWT 서명 비밀키가 유출되면 모든 토큰을 위조할 수 있으므로 비밀키 보관·교체 절차가 필요하다(`SESSION_SECRET`을 대체할 환경변수 정의 포함).
- 토큰 만료 시간을 길게 잡으면 유출된 토큰이 오래 악용될 수 있다.

## Implementation

- [ ] 구현 작업: `src/auth.js`의 express-session 미들웨어를 jsonwebtoken 기반 검증 미들웨어(`Authorization: Bearer` 헤더 검증)로 교체하고, 파트너용 토큰 발급 경로를 정의
- [ ] 테스트: 유효 토큰, 만료 토큰, 서명 불일치 토큰, 헤더 누락 케이스에 대한 인증 테스트
- [ ] 모니터링: 인증 실패(401) 비율과 토큰 만료로 인한 실패 추이 관찰
- [ ] 문서/설정 업데이트: `SESSION_SECRET` 대신 JWT 서명용 환경변수 정의, 파트너 연동 가이드에 토큰 발급·전송 방식 기재

## Reversibility

- **Reversible:** Partial
- **Rollback:** 현재는 `package.json`만 바뀐 상태라 `git checkout HEAD -- package.json`으로 express-session ^1.18.0을 복원하면 된다(`src/auth.js`는 아직 세션 방식). 다만 파트너사가 JWT로 연동한 뒤에는 파트너 쪽 인증 코드도 되돌려야 한다.
- **Migration Cost:** Low (현재 기준. 파트너 연동 이후에는 Medium)

## Review Trigger

- 키 발급·회전을 대신 처리해 줄 수단(시크릿 관리 도구, API 게이트웨이 등)이 도입되어 회전 관리를 직접 만들 필요가 없어질 때

## References

- **Documentation:** 기준 커밋 cd54b25(feat: 파트너 주문 조회 API), 변경 파일 `package.json`(커밋 전), 영향 파일 `src/auth.js`
