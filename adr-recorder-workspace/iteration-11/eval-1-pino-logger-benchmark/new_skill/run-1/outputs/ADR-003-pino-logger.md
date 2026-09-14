# ADR-003: 로거를 winston에서 pino로 교체

- **Status:** Proposed
- **Date:** 2026-09-14
- **Decision:** order-api의 로깅 라이브러리를 winston에서 pino로 교체한다.
- **Scope:** order-api (로깅 모듈 `src/logger.js`)
- **Decision Source:** Human

---

## Context

### Problem

order-api는 로깅 라이브러리로 winston(^3.13.0)을 사용해 왔다. API 서버를 autocannon으로 부하 테스트해 보니 winston 구성의 p99 지연과 처리량이 pino 구성보다 나빠서 로거 교체를 검토했다.
현재 저장소 상태: package.json은 pino로 바뀌었지만 `src/logger.js`는 아직 `require('winston')`을 사용한다(코드 전환이 끝나지 않음).

### Constraints

- 후보 라이브러리는 유지보수가 계속되고 있어야 한다(마지막 릴리스가 3년 전인 bunyan을 뺀 기준).
- 로거는 `src/logger.js`가 export하는 단일 인스턴스이고, 호출부(`src/server.js`)는 `logger.info(...)` 형태로 사용한다.

## Decision

### Selected

- **Technology:** pino ^9.4.0 (개발용 출력 포매터 pino-pretty ^11.2.2는 devDependencies)
- **Architecture:** 기존과 같이 `src/logger.js`가 로거 인스턴스 하나를 export하고, 애플리케이션 코드는 이를 require해서 쓴다.
- **Implementation:** package.json 의존성 교체 완료(winston 제거, pino·pino-pretty 추가). `src/logger.js`의 winston 구성(level `info`, JSON 포맷, Console transport)을 pino 인스턴스로 전환하는 작업이 남아 있다.

## Rationale

1. autocannon 측정에서 pino가 winston보다 우세했다. p99 지연은 38ms → 21ms(약 45% 감소), 처리량은 8.2k → 11.5k req/s(약 40% 증가)였다.
2. 다른 후보였던 bunyan은 마지막 릴리스가 3년 전이라 제외했고, 남은 선택지 중 pino를 골랐다.

## Evidence

- **Benchmark:** order-api 서버 autocannon 측정. winston: p99 38ms, 처리량 8.2k req/s. pino: p99 21ms, 처리량 11.5k req/s. (측정 조건인 연결 수·지속 시간·대상 엔드포인트는 기록되지 않음)

## Alternatives

### winston 유지 (현행)

- **Pros:** `src/logger.js`가 이미 winston으로 구성되어 있어 코드를 바꿀 필요가 없다.
- **Cons:** autocannon 측정에서 p99 38ms, 8.2k req/s로 pino(21ms, 11.5k req/s)보다 나빴다.
- **Rejected because:** 같은 서버 벤치마크에서 pino보다 p99 지연이 17ms 높고 처리량이 3.3k req/s 낮았다.

### bunyan

- **Cons:** 마지막 릴리스가 3년 전이다.
- **Rejected because:** 마지막 릴리스가 3년 전이라 유지보수 리스크가 있어 후보에서 뺐다.
- **Recheck if:** bunyan 유지보수가 재개되면 다시 검토한다.

## Consequences

### Positive

- 측정 기준으로 p99 지연 약 45% 감소, 처리량 약 40% 증가를 기대할 수 있다.
- 개발 환경에서는 pino-pretty로 사람이 읽기 쉬운 로그 출력을 쓸 수 있다.

### Negative

- `src/logger.js` 전환 작업과, winston 기준으로 작성된 로그 호출부 점검이 필요하다.

### Risks

- package.json에서 winston은 빠졌지만 `src/logger.js`는 아직 `require('winston')`을 사용한다. 이 상태로 의존성을 새로 설치하고 서버를 띄우면 모듈을 찾지 못해 기동에 실패한다. logger.js를 전환하기 전에는 배포하면 안 된다.
- 로그 출력 형식이 바뀐다. winston json은 `level: "info"`, `message`를 쓰고, pino 기본값은 숫자 `level`(info=30), `msg`를 쓰며 `time`·`pid`·`hostname`이 추가된다. 로그 수집·검색·알림이 필드명에 의존하고 있으면 영향을 받는다.
- pino-pretty는 devDependencies에만 있다. 운영 환경에서 pretty transport를 켜도록 구성하면 `--omit=dev` 설치 시 기동에 실패한다.

## Implementation

- [x] package.json 의존성 교체 (winston 제거, pino ^9.4.0·pino-pretty ^11.2.2 추가)
- [ ] `src/logger.js`를 pino 인스턴스로 전환 (level `info`, stdout JSON 출력 유지)
- [ ] 테스트: 서버 기동과 로그 출력 확인, jest 테스트 통과 확인
- [ ] 모니터링: 배포 후 운영 환경의 p99 지연·처리량이 벤치마크 결과와 맞는지 확인
- [ ] 문서/설정 업데이트: 로그 수집 파이프라인의 필드 매핑(`level`, `msg`) 점검, 개발 환경의 pino-pretty 사용 방법 정리

## Reversibility

- **Reversible:** Yes
- **Rollback:** `git checkout f057b95 -- package.json src/logger.js` 후 `npm install`로 winston 구성을 복원한다(두 파일은 f057b95 이후 커밋에서 바뀐 적 없음, 2026-09-14 기준).
- **Migration Cost:** Low (로거 구성은 `src/logger.js` 한 파일, 호출부는 `src/server.js` 1곳)

## Review Trigger

- bunyan 유지보수가 재개되면 bunyan을 다시 검토한다.

## References

- **Documentation:** winston 도입 커밋 f057b95 (`package.json`, `src/logger.js` 포함, `git show --stat`으로 확인)
