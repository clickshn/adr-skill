# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 내부 서비스 간 동기 통신 (시행 구간: checkout ↔ inventory)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- 내부 호출 p99 지연 SLO: 100ms
- 플랫폼팀 인원 2명 (신규 인프라 운영 부담을 크게 늘릴 수 없음)
- 재고 데이터는 실시간성이 필요함
- 외부 공개 API는 REST로 유지

## Decision

### Selected

- **Technology:** gRPC + Protocol Buffers (proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST 유지
- **Implementation:** `proto/inventory.proto`에 `inventory.v1.InventoryService/GetStock` 정의, 2026-03-02부터 checkout ↔ inventory 구간에 시행 중

## Rationale

1. 병목 원인이 REST+JSON 직렬화 비용이므로, 바이너리 직렬화(protobuf)로 지연과 페이로드를 함께 줄일 수 있다.
2. 사내 부하테스트에서 p99가 SLO(100ms) 안으로 들어오고 페이로드도 약 60% 줄었다.
3. GraphQL 페더레이션은 현 인원으로 운영이 불가하고, REST 유지 + 캐싱은 재고 실시간성 때문에 캐시 무효화가 어려워 문제를 해결하지 못한다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (2026-02-18, k6 500 VU 10분, checkout → inventory 재고 조회): p99 180ms → 52ms, p50 41ms → 12ms, 평균 페이로드 4.8KB → 1.9KB(약 60% 감소). 원본 결정 로그(D-007)의 p99 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정(2026-02-11) 값이며, 벤치 문서의 최종값은 52ms다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 큼
- **Rejected because:** 현 인원(플랫폼팀 2명)으로는 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려움
- **Rejected because:** 캐시 무효화 문제로 실시간 재고 조회 요구를 충족할 수 없음

## Consequences

### Positive

- checkout → inventory 재고 조회 p99가 부하테스트 기준 SLO(100ms) 이내로 내려감 (180ms → 52ms)
- 호출당 페이로드가 약 60% 감소

### Negative

- 내부(gRPC)와 외부(REST) 두 가지 통신 방식을 함께 운영해야 함
- 서비스 간 계약을 `proto/` 아래 protobuf 스키마로 관리해야 함

### Risks

- 부하테스트는 checkout → inventory 재고 조회 한 구간만 측정했으므로, 다른 내부 구간으로 확대할 때 같은 효과가 난다는 근거는 아직 없음

## Implementation

- [x] `proto/inventory.proto` 정의 및 gRPC 재고 조회 엔드포인트 구현 (25dad14)
- [x] 부하테스트 수행 및 결과 문서화 (15d4779)
- [x] checkout ↔ inventory 구간 시행 (2026-03-02~)
- [ ] 나머지 내부 서비스 간 동기 호출 gRPC 전환

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 inventory 재고 조회 클라이언트를 REST 호출로 되돌린다. 현재 gRPC로 전환된 계약은 `InventoryService/GetStock` RPC 1개뿐이다(`proto/inventory.proto`). 저장소에는 inventory의 REST 핸들러 코드가 없어 기존 REST 엔드포인트가 남아 있는지는 확인하지 못했다.
- **Migration Cost:** Low

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션 재검토

## References

- **Documentation:** `docs/decisions.md` D-007 (2026-09-11 이관), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto`, 커밋 25dad14 (feat(inventory): gRPC 재고 조회 엔드포인트), 15d4779 (docs: gRPC 부하테스트 결과 추가)
