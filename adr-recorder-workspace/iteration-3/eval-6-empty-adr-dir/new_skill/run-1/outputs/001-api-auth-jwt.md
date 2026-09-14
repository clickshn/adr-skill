# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway API 인증을 express-session 쿠키 세션에서 jsonwebtoken 기반 JWT 인증으로 교체한다.
- **Scope:** partner-gateway / API 인증 미들웨어 (src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

파트너사 서버들이 API(예: 파트너 주문 조회 API, 99ddbca)에 붙기 시작하면서, express-session 쿠키 세션 기반 인증은 서버 간 연동에 번거롭다. 쿠키는 브라우저 클라이언트를 전제로 한 방식이라, 파트너 서버마다 쿠키를 받아 두었다가 다시 보내는 처리를 따로 해야 한다.

### Constraints

- 파트너사 서버가 API를 직접 호출하는 서버 간 연동을 지원해야 한다.
- 파트너별 API 키를 발급하면 키 회전 관리 체계를 따로 만들어야 하는데, 이 체계는 만들지 않는다.
- 기존 Express 4(`express ^4.19.2`) 스택 위에서 해결한다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 서버에 세션을 저장하지 않는 무상태 인증. 쿠키 대신 요청 헤더로 받은 JWT의 서명과 만료를 요청마다 검증한다.
- **Implementation:** package.json 의존성 교체는 끝났다(작업 트리, 미커밋). src/auth.js는 아직 express-session 미들웨어를 export하고 있어 jsonwebtoken 검증 미들웨어로 바꿔야 한다.

## Rationale

1. JWT는 쿠키 없이 요청 헤더로 전달되므로, 쿠키 세션 때문에 생기던 파트너 서버 연동의 번거로움이 사라진다.
2. 파트너용 API 키 발급 방식과 달리 파트너별 키 회전 관리 체계를 따로 만들 필요가 없다. 서명 키는 서버 쪽 비밀값 하나로 관리한다.
3. 세션과 API 키를 함께 운영하지 않고 인증 방식을 하나로 통일한다.

## Alternatives

### express-session 유지 + 파트너용 API 키 발급

- **Pros:** 기존 세션 인증(src/auth.js)을 그대로 두면서, 파트너 서버에는 쿠키 없이 쓸 수 있는 키를 줄 수 있다.
- **Cons:** 인증 방식이 세션과 API 키 두 가지로 나뉘고, 파트너별 키의 발급·폐기·회전 관리를 따로 구현해야 한다.
- **Rejected because:** 키 회전 관리를 따로 만들어야 해서 접었다.
- **Recheck if:** API 게이트웨이나 시크릿 매니저처럼 키 발급·회전을 대신 처리해 주는 인프라를 도입할 때. 또는 토큰 즉시 폐기 요구가 커져서 어차피 서버 쪽 상태 관리가 필요해질 때.

## Consequences

### Positive

- 파트너 서버가 쿠키를 처리하지 않고 토큰만으로 API를 호출할 수 있다.
- 서버 쪽 세션 저장소가 없으므로, 인스턴스를 늘려도 세션을 공유할 필요가 없다.
- 파트너별 API 키 회전 관리 체계를 만들지 않아도 된다.

### Negative

- 발급한 토큰은 만료 전까지 서버에서 바로 무효화하기 어렵다. 세션을 지우는 식의 즉시 로그아웃을 할 수 없다.
- 토큰 발급 경로와 만료·갱신 정책을 새로 설계해야 한다.
- src/auth.js를 다시 작성해야 한다.

### Risks

- 현재 작업 트리 상태로는 서버가 기동하지 않는다. package.json에서 express-session을 뺐는데 src/auth.js는 여전히 `require('express-session')`을 하고 있어서, 의존성을 다시 설치하면 서버 기동 시 `Cannot find module 'express-session'` 오류가 난다. auth.js 교체를 의존성 변경과 같은 커밋에 넣어야 한다.
- 서명 비밀값이 유출되면 모든 토큰을 위조할 수 있다. 서명 키도 결국 교체해야 하므로, 최소한의 교체 절차(환경변수 교체 후 기존 토큰 만료 대기)는 필요하다.
- JWT 검증 설정을 잘못할 위험이 있다(허용 알고리즘 미지정 등). `jwt.verify`에 `algorithms`를 명시해야 한다.

## Implementation

- [ ] src/auth.js를 express-session 미들웨어에서 jsonwebtoken `verify` 기반 미들웨어로 교체 (`algorithms` 명시, 만료 검사 포함)
- [ ] 파트너용 토큰 발급 경로와 만료(exp) 정책 정의
- [ ] `SESSION_SECRET` 환경변수를 JWT 서명용 비밀값으로 교체
- [ ] 테스트: 유효 토큰, 만료 토큰, 서명 불일치, 헤더 누락
- [ ] 모니터링: 토큰 검증 실패(401) 비율
- [ ] 문서/설정 업데이트: 파트너 연동 가이드에 토큰 발급·전달 방식 안내

## Reversibility

- **Reversible:** Partial
- **Rollback:** 지금은 미커밋 상태인 package.json 변경만 되돌리면 된다(`git checkout HEAD -- package.json`). src/auth.js는 아직 세션 코드 그대로다. JWT 인증을 배포해서 파트너가 토큰 방식으로 연동한 뒤에는 파트너 쪽 인증 처리도 함께 되돌려야 한다.
- **Migration Cost:** Medium (배포 전에는 Low)

## Review Trigger

- API 게이트웨이나 시크릿 매니저처럼 키 발급·회전을 대신 처리해 주는 인프라를 도입할 때
- 토큰 즉시 폐기 요구가 커져서 어차피 서버 쪽 상태 관리가 필요해질 때

## References

- **Documentation:** package.json 의존성 diff(작업 트리, 미커밋: express-session ^1.18.0 → jsonwebtoken ^9.0.2), 관련 커밋 99ddbca(feat: 파트너 주문 조회 API), 현행 세션 미들웨어 src/auth.js
