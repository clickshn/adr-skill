# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 REST+JSON에서 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 내부 서비스 간 동기 호출 (현재 시행 구간: checkout ↔ inventory)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 넘었다.

### Constraints

- 지연 SLO: p99 100ms
- 외부 공개 API는 REST를 유지해야 한다.
- 운영 인원: 플랫폼팀 2명 (D-007 담당 팀)
- 재고 데이터는 실시간성이 필요하다.

## Decision

### Selected

- **Technology:** gRPC (protobuf)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST로 분리 운영
- **Implementation:** `proto/inventory.proto`(`inventory.v1.InventoryService/GetStock`)로 재고 조회 RPC를 정의했고, 2026-03-02부터 checkout ↔ inventory 구간에서 시행 중

## Rationale

1. 사내 부하테스트에서 checkout → inventory 재고 조회 p99가 180ms에서 SLO(100ms) 이내로 줄었다.
2. 평균 페이로드 크기가 약 60% 줄었다.

## Evidence

- **Benchmark:** k6, 500 VU, 10분, checkout → inventory 재고 조회 (2026-02-18). REST+JSON은 p50 41ms / p99 180ms / 페이로드 4.8KB, gRPC는 p50 12ms / p99 52ms / 페이로드 1.9KB (약 60% 감소). 원본 D-007의 "p99 45ms"는 커넥션 풀 워밍업을 빠뜨린 1차 측정(2026-02-11) 값이며, 부하테스트 문서가 최종값으로 명시한 것은 52ms다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담
- **Rejected because:** 현 인원(플랫폼팀 2명)으로는 그 부담을 감당할 수 없다.
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어렵다.
- **Rejected because:** 캐시 무효화 문제로 재고 데이터의 실시간성을 보장하기 어렵다.

## Consequences

### Positive

- checkout → inventory 재고 조회 p99가 SLO 이내로 들어왔다 (부하테스트 기준 180ms → 52ms).
- 호출당 전송 페이로드가 약 60% 줄었다.

### Negative

- 내부(gRPC)와 외부(REST) 두 가지 통신 방식을 함께 운영해야 한다.
- 서비스 간 계약을 `.proto` 스키마로 관리해야 한다.

### Risks

- 결정 범위는 내부 동기 호출 전체지만 저장소에서 확인되는 gRPC 정의는 inventory 한 곳(`proto/inventory.proto`)뿐이다. 나머지 구간의 전환 시점은 기록되어 있지 않다.

## Implementation

- [x] 구현 작업: 재고 조회 RPC 정의(`proto/inventory.proto`) 및 checkout ↔ inventory 구간 전환 (2026-03-02 시행)
- [ ] 구현 작업: 나머지 내부 서비스 간 동기 호출 전환
- [x] 테스트: gRPC 전환 부하테스트 (`bench/grpc-loadtest-2026-02.md`)
- [ ] 모니터링: 운영 환경 p99 지연 추적 (원본 로그에 운영 수치 기록 없음)
- [ ] 문서/설정 업데이트

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 inventory 재고 조회 호출을 REST+JSON 경로로 되돌린다. 저장소에는 `.proto` 정의만 있고 서비스 코드는 없어서, inventory 쪽 REST 조회 경로가 남아 있는지는 확인하지 못했다. 되돌리면 피크 시간 p99가 다시 SLO를 넘을 수 있다.
- **Migration Cost:** Low

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:** `docs/decisions.md` D-007 (원본 결정 로그), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto`, 커밋 979e62c (proto·부하테스트 문서 최초 추가), 919fb33·4b0137d (gRPC 관련 커밋, 파일 변경 없음)
