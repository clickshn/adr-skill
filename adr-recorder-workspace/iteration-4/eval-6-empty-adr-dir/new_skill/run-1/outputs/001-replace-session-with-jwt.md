# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway API 인증 방식을 express-session 기반 쿠키 세션에서 jsonwebtoken 기반 JWT로 교체한다.
- **Scope:** partner-gateway / API 인증 (`src/auth.js`)
- **Decision Source:** Human

---

## Context

### Problem

partner-gateway는 지금까지 express-session 쿠키 세션으로 API 요청을 인증해 왔다(`src/auth.js`). 파트너사 서버들이 API에 붙기 시작하면서(예: 파트너 주문 조회 API, eed8db4), 브라우저가 아닌 서버 간 호출에서 쿠키를 받아 보관하고 다시 실어 보내는 쿠키 기반 흐름이 번거로워졌다.

### Constraints

- 호출 주체가 파트너사 서버(서버 간 통신)이므로 쿠키 저장·전송에 기대지 않는 인증 방식이 필요하다.
- 파트너 인증을 위해 키 회전 관리 같은 별도 관리 기능을 새로 만드는 부담은 피하고자 한다.
- 현재 구성은 Express 4(`express ^4.19.2`)이며, 세션 서명 비밀은 `SESSION_SECRET` 환경 변수로 주입된다.

## Decision

### Selected

- **Technology:** jsonwebtoken `^9.0.2` (express-session `^1.18.0` 제거)
- **Architecture:** 서버 측 세션 저장소와 쿠키 대신, 요청마다 전달되는 서명된 JWT를 검증하는 무상태(stateless) 인증으로 전환한다.
- **Implementation:** `package.json`에서 express-session을 빼고 jsonwebtoken을 추가했다(작업 트리 변경, 미커밋). `src/auth.js`는 아직 express-session 미들웨어를 그대로 쓰고 있어 JWT 검증 미들웨어로 교체해야 한다.

## Rationale

1. 파트너사 서버가 쿠키를 다룰 필요 없이 토큰을 요청에 실어 보내면 되므로, 서버 간 연동이 쿠키 세션보다 단순하다.
2. 세션 방식을 유지한 채 파트너 전용 API 키를 따로 발급하는 방식과 달리, 키 회전 관리 기능을 별도로 만들지 않아도 된다.

## Alternatives

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 express-session 인증을 그대로 두고, 파트너 호출만 API 키로 따로 인증할 수 있다.
- **Cons:** 발급한 API 키의 회전(교체·폐기) 관리를 따로 만들어야 하고, 인증 경로가 세션과 API 키 두 갈래로 나뉜다.
- **Rejected because:** 키 회전 관리를 따로 만들어야 해서 부담이 크다.
- **Recheck if:** 키 회전·폐기를 기성 기능으로 제공하는 기반(예: API 게이트웨이, 시크릿 매니저)을 도입해 별도 구현 부담이 없어지는 경우.

## Consequences

### Positive

- 파트너 서버 연동 시 쿠키 처리가 필요 없어진다.
- 서버 측 세션 상태가 없어져 인스턴스를 늘릴 때 세션 공유를 신경 쓰지 않아도 된다.

### Negative

- JWT는 발급 후 만료 전까지 서버에서 즉시 무효화하기 어렵다. 탈취·권한 회수에 대응하려면 짧은 만료 시간이나 폐기 목록 같은 장치가 필요하다.
- 기존 쿠키 세션으로 붙던 클라이언트가 있다면 토큰 방식으로 옮겨야 한다.

### Risks

- `src/auth.js`가 여전히 `require('express-session')`을 호출하므로, 지금 `package.json` 기준으로 의존성을 새로 설치하면 서버 기동 시 모듈을 찾지 못해 실패한다. `src/auth.js` 교체와 `package.json` 변경을 함께 커밋해야 한다.
- JWT 서명 키도 결국 교체가 필요할 수 있다. 서명 키 교체 절차를 정해 두지 않으면 기각한 대안의 "키 회전 관리" 문제가 서명 키 차원에서 다시 생긴다.

## Implementation

- [ ] `src/auth.js`의 express-session 미들웨어를 jsonwebtoken 기반 JWT 검증 미들웨어로 교체
- [ ] 파트너용 토큰 발급 경로와 만료 시간, 서명 알고리즘 정의
- [ ] 테스트: 유효 토큰 통과, 만료·위조·누락 토큰 거부
- [ ] 모니터링: 인증 실패·토큰 만료 응답 비율 관찰
- [ ] 문서/설정 업데이트: `SESSION_SECRET`을 JWT 서명 키 환경 변수로 대체, 파트너 연동 가이드에 토큰 사용법 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`을 HEAD로 되돌려 express-session을 복구하면 된다(`git checkout HEAD -- package.json` 후 재설치). 현재 `src/auth.js`는 아직 세션 방식이라 코드 롤백은 필요 없다.
- **Migration Cost:** Low (파트너사가 JWT로 연동을 마친 뒤에는 파트너 측 변경까지 필요해 비용이 커진다)

## Review Trigger

- 키 회전·폐기를 기성 기능으로 제공하는 기반(예: API 게이트웨이, 시크릿 매니저)을 도입해 별도 구현 부담이 없어지는 경우, 세션 유지 + 파트너용 API 키 방식을 다시 검토한다.

## References

- **Documentation:** `package.json` 작업 트리 diff(express-session 제거, jsonwebtoken 추가, 미커밋), `src/auth.js`, 커밋 5f0f7e0(partner-gateway 초기 구성), eed8db4(파트너 주문 조회 API)
