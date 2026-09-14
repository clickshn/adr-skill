# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-09-11
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 서비스 간 내부 통신 (2026-03-02부터 checkout ↔ inventory 구간 시행 중, 담당: 플랫폼팀)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- 내부 호출 지연 SLO: p99 100ms
- 플랫폼팀 인원이 2명이라 스키마 관리·게이트웨이 운영 여력이 제한적이다.
- 재고 데이터는 실시간성이 필요하다.

## Decision

### Selected

- **Technology:** gRPC + Protocol Buffers (proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Implementation:** `proto/inventory.proto`에 `inventory.v1.InventoryService.GetStock(GetStockRequest{sku}) → GetStockResponse{sku, quantity}`를 정의했다. 2026-03-02부터 checkout ↔ inventory 구간에 시행 중이다.

## Rationale

1. 사내 부하테스트(`bench/grpc-loadtest-2026-02.md`)에서 checkout → inventory 재고 조회의 p99가 SLO(100ms) 이내로 내려갔다 (180ms → 52ms, 최종 측정값).
2. 평균 페이로드 크기가 약 60% 줄었다 (4.8KB → 1.9KB).
3. 대안(GraphQL 페더레이션, REST 유지 + 응답 캐싱)은 운영 인원과 데이터 실시간성 제약 때문에 기각했다 (Alternatives 참조).

## Evidence

- **Benchmark:** k6, 500 VU, 10분, checkout → inventory 재고 조회 (2026-02-18 최종 측정). REST+JSON은 p50 41ms / p99 180ms / 평균 페이로드 4.8KB, gRPC는 p50 12ms / p99 52ms / 1.9KB였다 (페이로드 약 60% 감소). 원본 D-007에 적힌 p99 45ms는 커넥션 풀 워밍업이 빠진 1차 측정(2026-02-11) 값이며, 부하테스트 문서는 최종값을 52ms로 정정했다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리·게이트웨이 운영 부담
- **Rejected because:** 현 인원(플랫폼팀 2명)으로 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 캐시 무효화가 어려움
- **Rejected because:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려움

## Consequences

### Positive

- 부하테스트 기준으로 checkout → inventory 재고 조회 p99가 180ms에서 52ms로 내려가 SLO(100ms) 이내가 되었다.
- 평균 페이로드가 약 60% 줄었다.

### Negative

- 내부 통신(gRPC)과 외부 공개 API(REST), 두 프로토콜을 함께 운영해야 하고 `.proto` 스키마도 관리해야 한다.

### Risks

- 원본 기준으로 시행 범위는 checkout ↔ inventory 구간뿐이다. 다른 내부 동기 호출 구간이 전환될 때까지 REST와 gRPC가 섞여 있다.

## Implementation

- [x] 구현 작업: `proto/inventory.proto` 정의(InventoryService.GetStock), 2026-03-02부터 checkout ↔ inventory 구간 시행
- [ ] 구현 작업: 그 밖의 내부 서비스 간 동기 호출 구간 gRPC 전환
- [x] 테스트: k6 부하테스트 (`bench/grpc-loadtest-2026-02.md`)
- [ ] 모니터링: 피크 시간 p99 SLO(100ms) 준수 여부 추적 (저장소에서 관련 설정을 찾지 못함)
- [ ] 문서/설정 업데이트: `docs/decisions.md` D-007 원본 처리(삭제 또는 이관 표시), 원본의 p99 수치(45ms → 52ms) 정정 여부 결정

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 재고 조회 호출을 REST+JSON으로 되돌리고 `proto/inventory.proto` 기반 gRPC 엔드포인트를 제거한다. 되돌리면 피크 시간 p99 SLO 초과 문제가 다시 생긴다. 저장소에는 proto 정의만 있어서 inventory의 기존 REST 재고 조회 엔드포인트가 남아 있는지는 확인할 수 없다.
- **Migration Cost:** Low (현재 적용 범위는 checkout ↔ inventory 1구간, RPC 1개)

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:**
  - `docs/decisions.md` D-007 (원본 결정 로그. 확정일이 적혀 있지 않아 Date는 이관일 2026-09-11로 기록)
  - `bench/grpc-loadtest-2026-02.md` (부하테스트 결과)
  - `proto/inventory.proto` (gRPC 서비스 정의)
  - 커밋: 979e62c (위 파일 추가), 919fb33 `feat(inventory): gRPC 재고 조회 엔드포인트`, 4b0137d `docs: gRPC 부하테스트 결과 추가`. 919fb33과 4b0137d는 파일 변경이 없는 커밋이다.
