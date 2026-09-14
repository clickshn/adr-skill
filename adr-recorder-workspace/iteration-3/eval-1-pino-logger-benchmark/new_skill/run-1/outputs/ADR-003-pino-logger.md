# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-11
- **Decision:** order-api의 로깅 라이브러리를 winston 3에서 pino 9로 교체한다.
- **Scope:** order-api (로깅, `src/logger.js`)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 winston(`winston.format.json()` + Console transport, level `info`)으로 로그를 남기고 있다. autocannon 부하 테스트에서 winston 사용 시 p99 지연 38ms, 처리량 초당 8.2k req로, 로깅 오버헤드가 API 성능에 영향을 주고 있었다.

### Constraints

- 기존 로그 형태(JSON, stdout 출력, level `info`)를 유지해야 한다.
- 로거는 `src/logger.js`에서 단일 인스턴스로 export되어 `src/server.js`에서 `logger.info(...)`로 사용된다.
- 로깅 라이브러리는 유지보수가 지속되는 프로젝트여야 한다.

## Decision

### Selected

- **Technology:** pino ^9.4.0 (dependencies), pino-pretty ^11.2.2 (devDependencies)
- **Architecture:** `src/logger.js`가 pino 인스턴스를 export하는 기존 단일 로거 모듈 구조를 유지한다.
- **Implementation:** 운영 환경은 pino 기본 JSON 출력(stdout), 개발 환경에서만 pino-pretty로 사람이 읽기 쉬운 출력을 쓴다(pino-pretty는 devDependency이므로 운영 설치에는 포함되지 않음).

## Rationale

1. 자사 API 서버 벤치마크에서 pino가 winston 대비 p99 지연을 38ms → 21ms(약 45% 감소)로 낮췄다.
2. 같은 벤치마크에서 처리량이 초당 8.2k → 11.5k req(약 40% 증가)로 늘었다.
3. 유력 대안이던 bunyan은 유지보수가 멈춘 상태(마지막 릴리스 3년 전)여서 장기 의존성으로 부적합하다.

## Evidence

- **Benchmark:** autocannon, order-api 서버 대상. winston: p99 38ms / 8.2k req/s → pino: p99 21ms / 11.5k req/s. (연결 수·지속 시간·대상 엔드포인트 등 측정 조건은 기록되지 않음)

## Alternatives

### winston 유지 (현행)

- **Pros:** 이미 `src/logger.js`에 적용돼 있어 전환 비용이 없다.
- **Cons:** 벤치마크에서 p99 38ms, 8.2k req/s로 pino 대비 지연이 높고 처리량이 낮다.
- **Rejected because:** 동일 조건 벤치마크에서 pino 대비 p99 지연·처리량 모두 열세.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전으로 유지보수가 중단된 상태.
- **Rejected because:** 유지보수가 멈춘 라이브러리를 새로 도입할 수 없음.
- **Recheck if:** bunyan 유지보수가 재개(새 릴리스)되는 경우.

## Consequences

### Positive

- API p99 지연 감소와 처리량 증가(벤치마크 기준 p99 -17ms, +3.3k req/s).
- stdout JSON 출력이라는 형태는 그대로라 로그 파이프라인 구조는 바뀌지 않는다(필드명·level 표기 차이는 Implementation에서 확인).

### Negative

- winston과 pino는 로그 호출 시그니처가 다르다(winston `logger.info(msg, meta)` / pino `logger.info(obj, msg)`). 메타데이터를 넘기는 호출은 인자 순서를 바꿔야 한다.
- winston의 transport 기반 설정은 pino transport/destination 방식으로 다시 작성해야 한다.

### Risks

- 현재 `package.json`에서는 winston이 제거됐지만 `src/logger.js`는 아직 `require('winston')`을 사용한다. 이 상태로 새로 설치하면 서버 기동 시 `MODULE_NOT_FOUND`로 실패한다.
- pino-pretty가 devDependency이므로 운영 환경에서 pretty transport를 켜면 모듈을 찾지 못해 기동에 실패한다.
- 벤치마크 측정 조건이 기록되지 않아 이후 재측정 시 동일 조건 비교가 어려울 수 있다.

## Implementation

- [ ] `src/logger.js`를 winston에서 pino로 교체 (level `info`, JSON 출력 유지)
- [ ] 개발 환경(NODE_ENV)에서만 pino-pretty transport 사용하도록 분기
- [ ] 서버 기동 및 `/health` 호출 시 로그 출력 확인, `npm test` 통과 확인
- [ ] 배포 후 p99 지연·처리량을 벤치마크 수치(p99 21ms, 11.5k req/s)와 비교 모니터링
- [ ] 로그 수집/조회 쪽 필드 차이(pino 기본 필드 `level` 숫자값, `time`, `pid`, `hostname`) 반영 여부 확인

## Reversibility

- **Reversible:** Yes
- **Rollback:** `package.json`에서 pino/pino-pretty를 제거하고 `winston: ^3.13.0`을 복원한 뒤 `src/logger.js`를 winston 설정으로 되돌린다(`git checkout fe5fe7e -- package.json src/logger.js`).
- **Migration Cost:** Low (로거 생성부 `src/logger.js` 1곳, 호출부 `src/server.js` 1곳)

## Review Trigger

- bunyan 유지보수가 재개(새 릴리스)되는 경우.
