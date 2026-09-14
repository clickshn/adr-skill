# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST로 유지한다.
- **Scope:** checkout-platform / 내부 서비스 간 동기 통신 (현재 checkout ↔ inventory 구간 시행 중)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- p99 지연 SLO 100ms
- 외부 공개 API는 REST를 유지해야 한다
- 플랫폼팀 인원 2명으로 운영 부담이 큰 방식은 감당 불가
- 재고 데이터는 실시간성이 필요하다

## Decision

### Selected

- **Technology:** gRPC + Protocol Buffers (proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST 유지
- **Implementation:** 2026-03-02부터 checkout ↔ inventory 구간에 시행. `proto/inventory.proto`의 `inventory.v1.InventoryService/GetStock` RPC로 재고를 조회한다.

## Rationale

1. 사내 부하테스트에서 재고 조회 p99가 180ms에서 52ms로 줄어 SLO(100ms)를 충족한다.
2. 평균 페이로드가 4.8KB에서 1.9KB로 약 60% 감소해 주문당 6회 호출의 직렬화·전송 비용이 줄어든다.
3. 외부 공개 API는 REST로 유지하므로 외부 클라이언트에 영향이 없다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (2026-02-18, k6, 500 VU, 10분, checkout → inventory 재고 조회) 결과, REST+JSON은 p50 41ms / p99 180ms / 4.8KB, gRPC는 p50 12ms / p99 52ms / 1.9KB. 원본 D-007에는 gRPC p99가 45ms로 적혀 있지만, 이 값은 커넥션 풀 워밍업이 빠진 1차 측정(2026-02-11) 값이다. 벤치 문서의 최종값은 52ms이다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담
- **Rejected because:** 현 인원(플랫폼팀 2명)으로 운영 부담을 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터의 실시간성 요구로 캐시 무효화가 어려움
- **Rejected because:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려움

## Consequences

### Positive

- 재고 조회 p99가 SLO 이내로 내려간다(벤치 기준 52ms, SLO 100ms).
- 페이로드 크기가 약 60% 줄어든다.

### Negative

- 내부는 gRPC, 외부는 REST로 두 프로토콜을 함께 운영해야 한다.
- 서비스 간 계약을 `.proto` 스키마로 관리하고 버전(`inventory.v1`)을 관리해야 한다.

### Risks

- 근거 수치는 부하테스트 값이다. 시행 이후 프로덕션 p99 실측값은 결정 로그에 기록돼 있지 않다.
- 1차 측정(45ms)과 최종 측정(52ms)의 차이처럼, 커넥션 풀 워밍업 같은 클라이언트 설정에 따라 지연이 달라질 수 있다.

## Implementation

- [x] checkout → inventory gRPC 재고 조회 엔드포인트 구현 (`proto/inventory.proto`, 5c5b5a7)
- [x] 부하테스트 (`bench/grpc-loadtest-2026-02.md`, 4a82687)
- [ ] 나머지 내부 서비스 간 동기 호출을 gRPC로 전환
- [ ] 프로덕션 p99 모니터링 (SLO 100ms 기준)

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 inventory 호출을 REST+JSON 클라이언트로 되돌린다. 되돌리면 SLO 초과 문제(REST p99 180ms)가 다시 생긴다.
- **Migration Cost:** Low (현재는 checkout ↔ inventory 1개 구간, RPC 1개(`GetStock`)만 전환된 상태이며, 전환 구간이 늘수록 비용이 커진다)

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:** `docs/decisions.md` D-007 (원본 결정 로그), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto`, 커밋 5c5b5a7 (feat(inventory): gRPC 재고 조회 엔드포인트), 4a82687 (docs: gRPC 부하테스트 결과 추가)
