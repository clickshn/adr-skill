# ADR-001: API 인증을 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** partner-gateway의 API 인증을 express-session 기반 쿠키 세션에서 JWT(jsonwebtoken)로 교체한다.
- **Scope:** partner-gateway / API 인증
- **Decision Source:** Human

---

## Context

### Problem

파트너사 서버들이 partner-gateway API에 직접 붙기 시작하면서, 브라우저를 전제로 한 쿠키 기반 세션 인증이 번거로워졌다. 서버 대 서버 호출에서는 쿠키 저장·전달을 각 파트너사가 따로 처리해야 한다.

### Constraints

- 현재 인증은 `src/auth.js`의 express-session 미들웨어 하나로 구성되어 있고, 세션 시크릿은 `SESSION_SECRET` 환경변수를 쓴다.
- 파트너사는 외부 조직이므로 인증 방식 변경 시 상대 서버의 연동 작업이 함께 필요하다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (package.json에 추가, express-session ^1.18.0 제거)
- **Architecture:** 서버 측 세션 저장소 없이, 요청마다 Authorization 헤더로 전달되는 JWT를 검증하는 무상태(stateless) 인증
- **Implementation:** `src/auth.js`의 express-session 미들웨어를 JWT 검증 미들웨어로 교체 (package.json 의존성 교체는 작업 트리에 반영됨, `src/auth.js`는 아직 세션 코드 상태)

## Rationale

1. 파트너사 서버 간 호출에서는 쿠키 왕복 없이 헤더에 토큰만 실으면 되므로 연동이 단순해진다.
2. 무상태 방식이라 게이트웨이 쪽에 세션 저장소를 유지할 필요가 없다.
3. 대안이었던 API 키 방식과 달리, 키 회전 관리 체계를 별도로 구축하지 않아도 토큰 만료(exp)로 수명을 다룰 수 있다.

## Alternatives

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 express-session 기반 인증을 그대로 두고, 파트너사에만 별도 자격증명을 내주면 된다.
- **Cons:** 키 회전(rotation) 관리 체계를 새로 만들어야 한다.
- **Rejected because:** 키 회전 관리를 따로 구축해야 하는 부담 때문에 접었다.

## Consequences

### Positive

- 파트너사 서버 연동 시 쿠키 처리 없이 헤더 토큰만으로 인증이 가능해진다.
- 게이트웨이가 무상태가 되어 세션 저장소 운영 부담이 사라진다.

### Negative

- 발급된 JWT는 만료 전까지 서버에서 즉시 무효화하기 어렵다(블랙리스트 등 별도 장치 필요).
- 토큰 서명 키 관리와 만료 정책을 새로 정해야 한다.

### Risks

- 현재 `src/auth.js`는 여전히 `express-session`을 require한다. package.json에서 의존성만 제거된 상태라 이 코드를 교체하기 전에는 애플리케이션이 기동되지 않는다.
- 파트너사 연동이 진행된 뒤에는 인증 방식 변경이 외부 조직의 작업을 동반하므로 되돌리기 비용이 올라간다.

## Implementation

- [ ] `src/auth.js`를 JWT 검증 미들웨어로 교체 (서명 키/만료 정책 포함)
- [ ] 인증 성공·실패 경로 테스트
- [ ] 인증 실패율 모니터링
- [ ] 파트너사용 연동 문서 및 환경변수 설정(SESSION_SECRET → JWT 서명 키) 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** package.json에서 jsonwebtoken을 제거하고 express-session ^1.18.0을 복원한다. 아직 커밋되지 않은 작업 트리 변경이므로 현재 시점에서는 HEAD(abe4c7c) 기준으로 되돌리면 된다.
- **Migration Cost:** Low (파트너사 연동이 실제로 이뤄지기 전 기준)

## References

- **Documentation:**
  - `package.json` — jsonwebtoken 추가 / express-session 제거 (미커밋 작업 트리)
  - `src/auth.js` — 교체 대상인 현행 세션 미들웨어
