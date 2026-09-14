# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway API 인증을 express-session 쿠키 세션 대신 jsonwebtoken 기반 JWT로 한다
- **Scope:** partner-gateway / API 인증 계층 (`src/auth.js`, `package.json`)
- **Decision Source:** Human

---

## Context

### Problem

partner-gateway의 API 인증은 현재 `express-session` 쿠키 세션(`src/auth.js`, `SESSION_SECRET`)으로 되어 있다. 파트너사 서버가 API를 직접 호출하기 시작하면서(최근 커밋 `eed8db4 feat: 파트너 주문 조회 API`) 서버 간 호출에서 쿠키를 받아 보관하고 다시 보내는 방식이 번거로워졌다.

### Constraints

- 호출 주체가 브라우저가 아니라 파트너사 서버다. 쿠키 저장·전송을 전제로 한 인증은 이 호출 방식과 맞지 않는다.
- 파트너용 자격 증명에 대해 키 회전을 관리하는 기능이 따로 없다. 이걸 새로 만들어야 하는 방식은 피하고 싶다.
- 기존 앱은 Express 4(`express ^4.19.2`) 기반이다.

## Decision

### Selected

- **Technology:** `jsonwebtoken ^9.0.2` (추가), `express-session ^1.18.0` (제거)
- **Architecture:** 서버 측 세션 저장소와 쿠키를 쓰는 대신, 요청마다 JWT를 받아 검증하는 무상태(stateless) 인증으로 바꾼다
- **Implementation:** `package.json`에서 의존성은 이미 교체됨. `src/auth.js`는 아직 `express-session`을 require하고 있어 JWT 검증 미들웨어로 바꿔야 한다

## Rationale

1. 파트너사 서버 간 호출에서는 쿠키 기반 세션이 번거롭다. JWT는 요청에 토큰만 실어 보내면 되므로 서버 간 호출에 더 잘 맞는다.
2. 세션을 유지한 채 파트너용 API 키를 따로 발급하는 방법은 키 회전 관리를 새로 만들어야 한다. JWT 전환 쪽이 추가로 만들 것이 적다.

## Alternatives

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 express-session 기반 인증 코드를 그대로 둘 수 있다
- **Cons:** 파트너용 키 발급과 키 회전 관리를 따로 만들어야 한다. 세션 인증과 API 키 인증, 두 체계를 함께 운영하게 된다
- **Rejected because:** 키 회전 관리를 별도로 구축해야 해서
- **Recheck if:** 키 발급·회전 관리를 직접 만들지 않아도 되는 수단(예: 키 관리 기능이 있는 게이트웨이나 외부 서비스)을 쓸 수 있게 될 때

## Consequences

### Positive

- 파트너사 서버가 쿠키를 다루지 않고 토큰만으로 API를 호출할 수 있다
- 서버가 세션 상태를 저장하지 않아도 된다

### Negative

- 한 번 발급한 토큰은 만료 전까지 서버가 바로 무효화하기 어렵다. 즉시 차단이 필요하면 별도 장치(짧은 만료, 차단 목록 등)가 필요하다
- 기존 세션 기반 클라이언트가 있다면 새 인증 방식으로 옮겨야 한다

### Risks

- 현재 작업 트리에서는 `package.json`에서 `express-session`이 빠졌는데 `src/auth.js`는 아직 `require('express-session')`을 하고 있다. 이 상태로 새로 설치하면 모듈을 찾지 못해 앱이 뜨지 않는다
- 파트너용 API 키 대안에서 문제였던 "키 회전"은 JWT 서명 키에도 여전히 있다. 서명 키가 유출되거나 교체해야 할 때의 절차가 필요하다

## Implementation

- [ ] `src/auth.js`를 express-session 미들웨어에서 JWT 검증 미들웨어(`jsonwebtoken`)로 교체하고, 파트너에게 토큰을 발급하는 경로를 마련
- [ ] 인증 테스트: 유효 토큰, 만료 토큰, 서명 불일치, 토큰 누락 케이스
- [ ] 모니터링: 인증 실패(401) 비율을 파트너별로 추적
- [ ] 문서/설정 업데이트: `SESSION_SECRET`을 JWT 서명용 비밀값 환경 변수로 교체하고, 파트너 연동 문서에 토큰 사용법을 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `git -C <repo> checkout HEAD -- package.json`으로 `express-session` 의존성을 되돌리면 된다. `src/auth.js`는 아직 세션 방식 그대로라 추가로 되돌릴 코드는 없다(JWT 미들웨어로 바꾼 뒤라면 해당 커밋을 revert)
- **Migration Cost:** Low (현재 시점 기준. 파트너사가 JWT로 연동을 마친 뒤에 되돌리면 파트너 쪽 수정도 필요해서 비용이 커진다)

## Review Trigger

- 키 발급·회전 관리를 직접 만들지 않아도 되는 수단(예: 키 관리 기능이 있는 게이트웨이나 외부 서비스)을 쓸 수 있게 될 때 → 세션 유지 + 파트너용 API 키 방식을 다시 검토한다
