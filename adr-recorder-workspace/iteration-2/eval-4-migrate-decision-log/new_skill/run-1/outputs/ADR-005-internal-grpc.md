# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 내부 서비스 간 동기 통신 (2026-03-02부터 checkout ↔ inventory 구간 시행 중)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- 피크 시간 p99 지연 SLO 100ms
- 외부 공개 API는 REST로 유지
- 플랫폼팀 인원 2명 (운영 부담이 큰 방식은 감당 불가)
- 재고 데이터는 실시간성이 필요함

## Decision

### Selected

- **Technology:** gRPC + protobuf (`inventory.v1.InventoryService/GetStock`)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST 유지
- **Implementation:** checkout ↔ inventory 재고 조회 구간부터 적용 (2026-03-02 시행)

## Rationale

1. 사내 부하테스트에서 checkout → inventory 재고 조회 p99가 180ms → 52ms로 줄어 SLO(100ms) 안에 들어온다.
2. 평균 페이로드 크기가 약 60% 감소(4.8KB → 1.9KB)해 주문당 6회 호출의 직렬화 비용이 줄어든다.

## Evidence

- **Benchmark:** k6, 500 VU, 10분, checkout → inventory 재고 조회 (2026-02-18) — REST+JSON p50 41ms / p99 180ms / 4.8KB, gRPC p50 12ms / p99 52ms / 1.9KB. 원본 D-007에는 gRPC p99가 45ms로 적혀 있으나, 이는 커넥션 풀 워밍업을 빠뜨린 1차 측정(2026-02-11) 값이고 재측정 최종값은 52ms다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담
- **Rejected because:** 그 운영 부담을 현 인원(플랫폼팀 2명)으로 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려움
- **Rejected because:** 실시간 재고 데이터에 대한 캐시 무효화 문제를 해결하기 어려움

## Consequences

### Positive

- checkout → inventory 재고 조회 p99 180ms → 52ms로 SLO(100ms) 충족
- 평균 페이로드 약 60% 감소

### Negative

- 내부(gRPC)와 외부(REST)로 통신 프로토콜이 이원화됨

### Risks

- 현재 시행 범위는 checkout ↔ inventory 구간뿐이라, 그 밖의 내부 동기 호출은 아직 REST로 남아 있음

## Implementation

- [x] inventory gRPC 재고 조회 엔드포인트 (`proto/inventory.proto`)
- [x] 전환 전후 부하테스트 (`bench/grpc-loadtest-2026-02.md`)
- [x] checkout ↔ inventory 구간 gRPC 시행 (2026-03-02~)
- [ ] 나머지 내부 서비스 간 동기 호출 gRPC 전환

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:** `docs/decisions.md` D-007 (2026-09-11 이관), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto`, 커밋 d6db083 (feat(inventory): gRPC 재고 조회 엔드포인트), cc95ed7 (docs: gRPC 부하테스트 결과 추가)
