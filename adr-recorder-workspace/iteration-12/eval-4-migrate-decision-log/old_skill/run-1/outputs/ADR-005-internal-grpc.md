# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용으로
피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- 외부 공개 API는 기존 클라이언트 호환성을 위해 REST를 유지해야 한다.
- 플랫폼팀 인원은 2명으로, 추가 게이트웨이·스키마 운영 부담을 감당하기 어렵다.

## Decision

### Selected

- **Technology:** gRPC (proto3 / protobuf) — 내부 동기 호출용
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST 유지 (이중 스택)
- **Implementation:** checkout ↔ inventory 구간부터 시행 (2026-03-02~). 스키마는
  `proto/inventory.proto`의 `inventory.v1.InventoryService.GetStock`.

## Rationale

1. 부하테스트에서 p99 지연이 180ms → 52ms로 감소해 SLO(100ms)를 충족한다.
2. 평균 페이로드가 4.8KB → 1.9KB로 약 60% 줄어 주문당 6회 호출의 누적 비용이 낮아진다.
3. 외부 공개 API를 REST로 유지하므로 외부 클라이언트 호환성에는 영향이 없다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (k6, 500 VU, 10분, checkout → inventory 재고 조회)
  — p50 41ms → 12ms, p99 180ms → 52ms, 평균 페이로드 4.8KB → 1.9KB.
  원본 결정 로그(D-007)에 적힌 "p99 45ms"는 커넥션 풀 워밍업이 누락된 1차 측정(2026-02-11)
  값이며, 재측정된 최종값은 52ms다.

## Alternatives

### GraphQL 페더레이션

- **Pros:** 클라이언트가 필요한 필드만 조회해 과다 전송을 줄일 수 있다.
- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 크다.
- **Rejected because:** 현 인원(플랫폼팀 2명)으로 스키마 관리·게이트웨이 운영을 감당할 수 없음.
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때.

### REST 유지 + 응답 캐싱

- **Pros:** 기존 스택을 그대로 두고 지연을 줄일 수 있다.
- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어렵다.
- **Rejected because:** 재고 데이터의 실시간성 요구로 캐시 무효화가 어려움.

## Consequences

### Positive

- checkout → inventory 경로의 p99 지연이 SLO(100ms) 안으로 들어온다.
- 페이로드 축소로 서비스 간 네트워크 전송량이 줄어든다.
- protobuf 스키마가 서비스 간 계약으로 명시된다.

### Negative

- 내부 gRPC와 외부 REST를 함께 운영하는 이중 스택이 된다.
- protobuf 스키마 관리와 코드 생성 파이프라인이 새로 필요하다.

### Risks

- 전환 구간이 늘어날수록 플랫폼팀 2명의 스키마·클라이언트 관리 부담이 커진다.
- 내부 REST 경로와 gRPC 경로가 공존하는 동안 두 경로의 동작이 어긋날 수 있다.

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 재고 조회 호출을 기존 내부 REST 엔드포인트로 되돌리고
  `proto/inventory.proto` 기반 생성 클라이언트를 제거한다. 현재 적용 구간이
  checkout ↔ inventory 한 곳이라 되돌릴 범위가 좁다.
- **Migration Cost:** Low

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:** `docs/decisions.md`의 D-007 (원본 결정 로그), `bench/grpc-loadtest-2026-02.md`,
  `proto/inventory.proto`. 세 파일 모두 커밋 `ac6b178`에 포함되어 있다.
