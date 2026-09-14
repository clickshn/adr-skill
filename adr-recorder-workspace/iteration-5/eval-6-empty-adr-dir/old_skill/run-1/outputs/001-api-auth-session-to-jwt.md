# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway API 인증 방식을 express-session 기반 쿠키 세션에서 jsonwebtoken 기반 JWT로 교체한다.
- **Scope:** partner-gateway / API 인증 (src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

파트너사 서버들이 API에 붙기 시작하면서(파트너 주문 조회 API, cd54b25), 쿠키 기반 세션 인증은 서버 간 연동에서 다루기 번거로워졌다.
현재 인증은 `src/auth.js`에서 `express-session` 미들웨어(`SESSION_SECRET`, `resave: false`, `saveUninitialized: false`)로 구성되어 있으며, 별도 세션 store 설정이 없어 기본 MemoryStore를 사용하는 상태다.

### Constraints

- 클라이언트가 브라우저가 아니라 파트너사 서버이므로, 쿠키 저장·재전송에 의존하지 않는 인증 수단이 필요하다.
- 파트너용 인증 수단을 도입하더라도 키 회전 같은 별도 관리 기능을 새로 만드는 부담은 피하고자 한다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 서버 측 세션 상태를 두지 않는 토큰 기반(stateless) 인증으로 전환
- **Implementation:** `package.json` 의존성 교체 완료. `src/auth.js`의 세션 미들웨어를 JWT 검증 미들웨어로 교체하는 작업은 남아 있음

## Rationale

1. 파트너사 서버 연동에서 쿠키 기반 세션이 번거로워, 쿠키 없이 요청마다 토큰을 실어 보내는 JWT가 서버 간 연동에 더 맞다.
2. 세션을 유지하면서 파트너용 API 키를 따로 발급하는 방식은 키 회전 관리를 별도로 만들어야 해서, 그 부담 없이 인증 방식을 하나로 정리할 수 있는 JWT를 택했다.

## Alternatives

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 express-session 기반 인증을 그대로 유지할 수 있다.
- **Cons:** 파트너용 API 키의 회전 관리를 별도로 만들어야 한다.
- **Rejected because:** 키 회전 관리 기능을 따로 구축해야 하는 부담 때문에 접었다.
- **Recheck if:** 키 발급·회전을 대신 처리해 줄 수단(기존 인프라나 관리 도구 등)이 생겨 별도 구축 부담이 사라질 때

## Consequences

### Positive

- 파트너사 서버가 쿠키 처리 없이 토큰만으로 API를 호출할 수 있다.
- 서버 측 세션 저장소가 필요 없어진다(현재 기본 MemoryStore 의존도 함께 사라짐).

### Negative

- 발급된 토큰은 만료 전까지 서버에서 즉시 무효화하기 어렵다.
- 기존 세션(쿠키) 기반으로 붙어 있던 클라이언트가 있다면 토큰 방식으로 전환해야 한다.

### Risks

- `package.json`에서는 express-session이 빠졌지만 `src/auth.js`는 여전히 `require('express-session')`을 하고 있어, 코드 전환 전에는 의존성 재설치 후 앱 기동 시 모듈 로드 오류가 난다.
- JWT 서명 키가 유출되면 임의의 토큰 위조가 가능하므로 서명 키 보관·교체 방안이 필요하다.

## Implementation

- [ ] `src/auth.js`의 express-session 미들웨어를 jsonwebtoken 기반 토큰 검증 미들웨어로 교체
- [ ] 파트너 서버용 토큰 발급 경로 및 만료 정책 정의
- [ ] 토큰 없음/만료/위조 케이스 테스트
- [ ] 인증 실패율 모니터링
- [ ] `SESSION_SECRET` 대신 JWT 서명 키 환경변수 설정, 파트너 연동 문서 업데이트

## Reversibility

- **Reversible:** Partial
- **Rollback:** `package.json`의 `jsonwebtoken ^9.0.2`를 `express-session ^1.18.0`으로 되돌리고 `src/auth.js`의 세션 미들웨어 구성을 복원한다. 현재는 코드가 아직 세션 기반이라 의존성만 되돌리면 되지만, 파트너사가 JWT로 연동한 뒤에는 파트너 측 인증 방식도 함께 되돌려야 한다.
- **Migration Cost:** Medium

## Review Trigger

- 키 발급·회전을 대신 처리해 줄 수단(기존 인프라나 관리 도구 등)이 생겨 별도 구축 부담이 사라질 때 (세션 유지 + 파트너용 API 키 발급 재검토)

## References

- **Documentation:** `package.json` 의존성 변경(미커밋, express-session ^1.18.0 → jsonwebtoken ^9.0.2), 관련 커밋 cd54b25 (feat: 파트너 주문 조회 API)
