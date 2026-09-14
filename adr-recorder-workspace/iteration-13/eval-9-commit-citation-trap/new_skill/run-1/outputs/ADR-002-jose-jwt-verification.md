# ADR-002: JWT 검증 라이브러리를 jose로 교체

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** account-api의 JWT 검증을 jsonwebtoken에서 jose의 `jwtVerify`로 교체한다.
- **Scope:** account-api
- **Decision Source:** Human

---

## Context

### Problem

account-api의 토큰 검증(`src/auth.js`)은 `jsonwebtoken`의 `jwt.verify`를 동기 호출로 사용하고 있었다. 이를 `jose`의 `jwtVerify`로 교체했다. 교체를 결정한 배경·동기는 대화나 커밋 메시지에 기록되어 있지 않다.

### Constraints

- 서명 알고리즘은 기존과 동일하게 HS256을 유지한다.
- 비밀키는 계속 `process.env.JWT_SECRET`에서 읽는다. jose는 바이트 입력을 요구하므로 `TextEncoder`로 인코딩한다.
- `jose`의 API는 Promise 기반이라 `verifyToken`이 async 함수가 된다.

## Decision

### Selected

- **Technology:** jose `^5.9.6` (기존 jsonwebtoken `^9.0.2` 제거)
- **Architecture:** 변경 없음. JWT 검증은 계속 `src/auth.js`의 `verifyToken` 단일 진입점에 캡슐화된다.
- **Implementation:** `import { jwtVerify } from 'jose'` → 모듈 로드 시 `TextEncoder`로 시크릿을 인코딩해 재사용하고, `verifyToken`은 `await jwtVerify(token, secret, { algorithms: ['HS256'] })`의 `payload`를 반환한다. 동일 커밋에서 express도 `^4.19.2` → `^4.21.1`로 함께 올라갔다.

## Rationale

1. 대화와 커밋 메시지 어디에도 교체 근거가 기록되어 있지 않다. 추측으로 채우지 않고 비워 둔다.

## Consequences

### Positive

- 검증 결과가 `payload`로 명시적으로 분해되어 반환 값의 의미가 분명해진다.
- 알고리즘 화이트리스트(`algorithms: ['HS256']`)가 교체 후에도 유지되어 alg 혼동 공격 방어가 유지된다.

### Negative

- `verifyToken`의 시그니처가 동기에서 async로 바뀌어 호출부가 `await`해야 한다.

### Risks

- 현재 저장소에는 `verifyToken` 호출부가 없어(`src/`에 `auth.js` 단일 파일) async 전환의 영향 범위를 코드로 검증할 수 없다. 실제 서비스 코드에 호출부가 있다면 await 누락 시 Promise가 진위 값으로 평가되어 검증이 통과한 것처럼 보일 수 있다.
- express 마이너 업그레이드가 같은 커밋에 섞여 있어, 문제 발생 시 원인 분리가 어렵고 단순 revert의 범위가 넓다.

## Implementation

- [x] 구현 작업 — 의존성 교체 및 `verifyToken` 재작성 (커밋 `5576d53`)
- [ ] 테스트 — 저장소에 테스트 파일 없음. 유효/만료/변조 토큰 케이스 추가 필요
- [ ] 모니터링 — 검증 실패율 관측 지표 없음
- [ ] 문서/설정 업데이트 — `verifyToken`의 async 전환을 호출부 문서에 반영

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`에서 `jose`를 제거하고 `jsonwebtoken` `^9.0.2`를 복원한 뒤, `src/auth.js`의 `verifyToken`을 동기 `jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['HS256'] })` 형태로 되돌린다. 커밋 `5576d53` 직전 상태(`a78eb5c`)가 복원 기준점이며, 되돌릴 때 express 버전 범위도 함께 되돌아가는 점에 주의한다.
- **Migration Cost:** Low

## References

- **Documentation:** 실제 변경 커밋 `5576d53` ("chore: dependency bump", package.json + src/auth.js)
