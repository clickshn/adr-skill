# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform (checkout ↔ inventory)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- 플랫폼팀 인원은 2명으로, 새 게이트웨이 계층을 운영할 여력이 없다.
- 재고 데이터는 실시간성이 필요해 응답 캐싱으로 완화하기 어렵다.
- 외부 공개 API는 기존 소비자 호환성을 위해 REST를 유지해야 한다.

## Decision

### Selected

- **Technology:** gRPC + protobuf (proto3), `inventory.v1.InventoryService`
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST로 이원화
- **Implementation:** `proto/inventory.proto`에 `GetStock(GetStockRequest) → GetStockResponse` 정의, checkout ↔ inventory 구간에 2026-03-02부터 시행

## Rationale

1. 부하테스트에서 p99 지연이 SLO(100ms) 아래로 내려가 문제의 원인을 직접 해소했다.
2. protobuf 직렬화로 페이로드가 약 60% 줄어 호출당 비용이 함께 감소했다.
3. 외부 API를 REST로 남겨 기존 소비자 호환성을 깨지 않으면서 내부 구간만 바꿀 수 있다.

## Evidence

- **Benchmark:** k6, 500 VU / 10분, checkout → inventory 재고 조회 기준 — p99 180ms → 52ms, p50 41ms → 12ms, 평균 페이로드 4.8KB → 1.9KB (약 60% 감소). 출처: `bench/grpc-loadtest-2026-02.md` (2026-02-18 최종 측정)

## Alternatives

### GraphQL 페더레이션

- **Pros:** 서비스 간 스키마를 통합해 클라이언트 질의를 단순화
- **Cons:** 스키마 관리와 게이트웨이 운영 부담
- **Rejected because:** 현 인원(플랫폼팀 2명)으로 운영 부담을 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어남

### REST 유지 + 응답 캐싱

- **Pros:** 기존 스택 변경 없이 호출 비용만 완화
- **Cons:** 캐시 무효화 설계가 필요
- **Rejected because:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려움

## Consequences

### Positive

- 재고 조회 구간 p99 지연이 SLO 이내로 복귀.
- 호출당 페이로드 감소로 네트워크 비용이 줄어듦.

### Negative

- 내부 gRPC와 외부 REST 두 가지 인터페이스를 동시에 유지해야 함.
- protobuf 스키마 버전 관리와 코드 생성 단계가 빌드에 추가됨.

### Risks

- proto 스키마 변경 시 서비스 간 배포 순서를 맞추지 않으면 호환성 문제가 발생할 수 있음.

## Implementation

- [x] 구현 작업 — `proto/inventory.proto` 정의 및 inventory gRPC 재고 조회 엔드포인트
- [x] 테스트 — k6 부하테스트 (`bench/grpc-loadtest-2026-02.md`)
- [ ] 모니터링
- [ ] 문서/설정 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 재고 조회 호출을 기존 REST 엔드포인트로 되돌리고 `proto/inventory.proto` 및 생성 코드를 제거. 외부 공개 API는 변경하지 않았으므로 영향 없음.
- **Migration Cost:** Medium

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:** `docs/decisions.md` D-007 (원본 결정 로그), `bench/grpc-loadtest-2026-02.md`
