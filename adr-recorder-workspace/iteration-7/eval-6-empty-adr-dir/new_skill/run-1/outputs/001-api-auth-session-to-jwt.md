# ADR-001: API 인증을 express-session 쿠키 세션에서 JWT로 전환

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** partner-gateway API 인증 방식을 express-session 기반 쿠키 세션에서 jsonwebtoken 기반 JWT로 바꾼다.
- **Scope:** partner-gateway / API 인증 (src/auth.js)
- **Decision Source:** Human

---

## Context

### Problem

파트너사 서버들이 API에 붙기 시작하면서 쿠키 기반 세션 인증이 번거로워졌다. 서버 간 호출에서 쿠키를 받아 유지·재전송하는 흐름이 파트너 연동에 맞지 않는다.

### Constraints

- 호출 주체가 브라우저가 아니라 파트너사 서버다.
- 파트너용 인증에 키 회전 관리 같은 별도 관리 기능을 새로 만들지 않는다.
- 현재 인증은 src/auth.js에서 express-session 미들웨어(`SESSION_SECRET`)로 구성되어 있다.

## Decision

### Selected

- **Technology:** jsonwebtoken ^9.0.2 (express-session ^1.18.0 제거)
- **Architecture:** 쿠키로 식별하는 서버 측 세션 대신, 요청마다 토큰을 실어 보내고 서버가 서명을 검증하는 방식
- **Implementation:** package.json에서 express-session을 빼고 jsonwebtoken을 추가함(커밋 전 작업 트리 변경). src/auth.js는 아직 express-session 미들웨어를 쓰고 있어 교체가 필요하다.

## Rationale

1. 파트너사 서버 연동에서는 쿠키 세션 유지가 번거롭고, 요청 단위 토큰이 서버 간 호출에 더 단순하다.
2. 세션 방식을 유지하면서 파트너용 API 키를 따로 두는 안은 키 회전 관리를 별도로 만들어야 해서, 인증 방식을 하나로 정리하는 편이 낫다고 판단했다.

## Alternatives

### 현행 유지 (express-session 쿠키 세션)

- **Pros:** 코드 변경이 없고, 이미 동작하는 인증 흐름을 그대로 쓴다.
- **Cons:** 파트너사 서버가 쿠키를 받아 유지·재전송해야 한다.
- **Rejected because:** 파트너사 서버들이 붙으면서 쿠키 기반이 번거로워졌다.

### 세션 방식 유지 + 파트너용 API 키 발급

- **Pros:** 기존 세션 인증을 건드리지 않고 파트너 경로만 추가한다.
- **Cons:** 인증 방식이 둘로 나뉘고, API 키 관리 기능이 새로 필요하다.
- **Rejected because:** 키 회전 관리를 따로 만들어야 해서 접었다.

## Consequences

### Positive

- 파트너사 서버가 쿠키 처리 없이 토큰만 실어 API를 호출할 수 있다.
- 인증 방식이 JWT 하나로 정리된다.

### Negative

- 서버 측 세션 저장소가 없어져, 발급한 토큰을 만료 전에 즉시 무효화하려면 별도 장치(짧은 만료, 폐기 목록 등)가 필요하다.
- 토큰 발급·검증 로직을 새로 작성해야 한다.

### Risks

- src/auth.js가 여전히 `require('express-session')`을 하고 있어, 현재 package.json 기준으로 새로 설치(npm install)하면 모듈을 찾지 못해 서버 기동이 실패한다.
- JWT 서명 비밀키도 유출·교체에 대비한 교체 절차가 필요할 수 있다. API 키 안을 기각한 사유(키 회전 관리)와 겹치므로 범위를 정해 둘 필요가 있다.

## Implementation

- [ ] src/auth.js를 express-session 미들웨어에서 JWT 검증 미들웨어로 교체
- [ ] 파트너용 토큰 발급 경로 구현, 서명 알고리즘·만료 시간 결정
- [ ] 서명 비밀키 환경변수 정의 (기존 `SESSION_SECRET` 대체 여부 포함)
- [ ] 테스트: 유효/만료/위조 토큰 케이스
- [ ] 모니터링: 토큰 검증 실패 건수
- [ ] 문서/설정 업데이트: 파트너 연동 가이드에 인증 방식 변경 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `git checkout HEAD -- package.json`로 express-session 의존성을 복원하면 된다(src/auth.js는 아직 세션 코드 그대로). 파트너가 JWT 연동을 마친 뒤에는 파트너 측 클라이언트 수정도 함께 되돌려야 한다.
- **Migration Cost:** Low
