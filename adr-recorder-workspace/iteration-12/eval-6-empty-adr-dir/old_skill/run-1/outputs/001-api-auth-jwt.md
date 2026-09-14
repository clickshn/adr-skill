# ADR-001: API 인증을 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** partner-gateway의 API 인증을 express-session 기반 쿠키 세션에서 jsonwebtoken 기반 JWT로 교체한다.
- **Scope:** partner-gateway (API 인증 계층)
- **Decision Source:** Human

---

## Context <!-- 필수 -->

### Problem

파트너사 서버들이 partner-gateway API에 연동되기 시작하면서, 기존 쿠키 세션 방식이 번거로워졌다.
현재 인증은 `src/auth.js`에서 `express-session` 미들웨어 하나로 구성되어 있고, 브라우저 쿠키를
전제로 한다. 서버 대 서버로 호출하는 파트너사 입장에서는 쿠키 저장·전달을 직접 다뤄야 한다.

### Constraints

- 파트너사는 브라우저가 아닌 서버에서 호출하므로 쿠키 전달을 전제할 수 없다.
- 파트너별 인증 수단을 새로 운영해야 한다면 회전(rotation)·폐기 관리 체계가 함께 필요하다.
- 현재 인증 구현은 `src/auth.js` 한 파일에 모여 있어 교체 지점이 좁다.

## Decision <!-- 필수 -->

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (기존 express-session ^1.18.0 제거)
- **Architecture:** 서버 측 세션 저장소에 의존하던 상태 기반 인증을, 토큰 자체가 신원을 담는
  무상태(stateless) 인증으로 전환한다. 파트너사 서버는 발급받은 JWT를 요청 헤더로 전달한다.
- **Implementation:** `package.json`에서 `express-session`을 빼고 `jsonwebtoken`을 추가했다.
  `src/auth.js`의 세션 미들웨어는 아직 교체 전이며, JWT 검증 미들웨어로 다시 작성해야 한다.

## Rationale <!-- 필수 -->

1. 파트너사 서버 연동이 늘어나는 상황에서 쿠키 기반 인증은 호출 측 부담이 크다. JWT는 헤더로
   전달되므로 서버 대 서버 호출에 그대로 맞는다.
2. 무상태 토큰이라 게이트웨이 측에 세션 저장소를 유지할 필요가 없다.
3. 대안이던 파트너용 API 키 발급은 키 회전 관리 체계를 따로 만들어야 해서, 지금 감당할 범위를
   넘는다. JWT는 만료(exp)가 토큰 규격 자체에 들어 있어 별도 회전 체계 없이 수명을 다룰 수 있다.

## Alternatives <!-- 발견 가능한 경우만 -->

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 express-session 기반 인증을 그대로 두고, 파트너사에만 별도 자격증명을 내주면
  되므로 기존 브라우저 클라이언트 경로를 건드리지 않는다.
- **Cons:** 키 회전·폐기 관리 체계를 새로 만들어야 한다. 인증 경로가 세션과 API 키 둘로 갈린다.
- **Rejected because:** 키 회전 관리를 따로 구축해야 하는 부담 때문에 접었다.

## Consequences <!-- 필수 -->

### Positive

- 파트너사 서버가 쿠키 처리 없이 헤더만으로 인증할 수 있다.
- 게이트웨이가 세션 상태를 들고 있지 않아도 되어 인증 계층이 단순해진다.
- 인증 경로가 하나(JWT)로 유지되어 API 키 체계를 따로 운영하지 않아도 된다.

### Negative

- 발급된 JWT는 만료 전까지 서버에서 즉시 무효화하기 어렵다. 세션 삭제로 즉시 로그아웃시키던
  동작을 그대로 재현할 수 없다.
- 기존 쿠키 세션에 의존하던 클라이언트가 있다면 함께 전환해야 한다.

### Risks

- `SESSION_SECRET`을 쓰던 자리에 JWT 서명 키 관리가 새로 들어온다. 키 유출 시 영향 범위가
  세션 시크릿보다 넓다.
- `src/auth.js`가 아직 express-session을 `require`하는데 `package.json`에서는 해당 의존성이
  빠져 있어, 현재 상태로는 런타임에서 모듈을 찾지 못한다. 코드 교체 전까지는 불일치 상태다.
- 토큰 만료 시간을 길게 잡으면 탈취 시 노출 기간이 길어진다.

## Implementation <!-- 구현 결정일 때만 -->

- [ ] `src/auth.js`를 JWT 검증 미들웨어로 교체 (express-session `require` 제거)
- [ ] JWT 서명 키 및 만료 정책 설정 (`SESSION_SECRET` 대체 환경 변수)
- [ ] 파트너사용 토큰 발급 경로 정의
- [ ] 인증 성공/실패 경로 테스트
- [ ] 인증 실패율 모니터링
- [ ] 파트너 연동 문서에 헤더 기반 인증 방식 반영

## Reversibility <!-- 가능하면 항상 -->

- **Reversible:** Yes
- **Rollback:** `package.json`에서 `jsonwebtoken`을 빼고 `express-session ^1.18.0`을 되돌린다.
  `src/auth.js`는 아직 세션 미들웨어 그대로이므로 코드 변경 없이 원복된다. 파트너사에 JWT를
  발급한 뒤라면 연동 측 협의가 추가로 필요하다.
- **Migration Cost:** Low
