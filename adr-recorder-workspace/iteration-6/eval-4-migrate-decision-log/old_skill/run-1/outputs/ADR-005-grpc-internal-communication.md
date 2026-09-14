# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-09-11
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform / 내부 서비스 간 동기 호출 (현재 checkout ↔ inventory 구간 시행 중)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- p99 지연 SLO 100ms
- 외부 공개 API는 REST 유지
- 플랫폼팀 인원 2명 (운영 부담이 큰 방식은 감당 불가)
- 재고 데이터는 실시간성이 필요함

## Decision

### Selected

- **Technology:** gRPC + Protocol Buffers (proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST 유지
- **Implementation:** `proto/inventory.proto`의 `inventory.v1.InventoryService.GetStock`으로 재고 조회. 2026-03-02부터 checkout ↔ inventory 구간 시행 중 (원본 결정 로그 D-007 기준)

## Rationale

1. 사내 부하테스트에서 gRPC 전환 시 p99가 180ms → 52ms로 줄어 SLO(100ms) 안에 들어온다.
2. 평균 페이로드 크기가 약 60% 감소한다(4.8KB → 1.9KB).
3. 외부 공개 API는 REST로 유지하므로 외부 소비자에게 영향이 없다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (2026-02-18, k6 500 VU 10분, checkout → inventory 재고 조회). REST+JSON p50 41ms / p99 180ms / 평균 페이로드 4.8KB → gRPC p50 12ms / p99 52ms / 1.9KB. 원본 결정 로그(D-007)의 "p99 45ms"는 커넥션 풀 워밍업을 빠뜨린 1차 측정(2026-02-11) 값이고, 벤치 문서의 최종값은 52ms다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담
- **Rejected because:** 현 인원(플랫폼팀 2명)으로 스키마 관리·게이트웨이 운영 부담을 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Cons:** 캐시 무효화가 어려움
- **Rejected because:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려움

## Consequences

### Positive

- checkout → inventory 재고 조회 p99가 SLO 안으로 들어온다(부하테스트 기준 52ms).
- 페이로드 크기 감소로 직렬화·전송 비용이 줄어든다.
- protobuf 스키마(`proto/`)가 서비스 간 계약 역할을 한다.

### Negative

- 내부(gRPC)와 외부(REST) 두 가지 프로토콜을 함께 운영해야 한다.
- proto 스키마 버전(`inventory.v1`) 관리가 새로 필요해진다.

### Risks

- 현재는 checkout ↔ inventory 구간만 시행 중이라, 나머지 내부 동기 호출이 전환될 때까지 REST와 gRPC가 섞여 있다.

## Implementation

- [x] checkout ↔ inventory 재고 조회 gRPC 엔드포인트 (`proto/inventory.proto`, 커밋 c32c6dc), 2026-03-02부터 시행
- [x] 부하테스트 (`bench/grpc-loadtest-2026-02.md`, 커밋 102695e)
- [ ] 나머지 내부 서비스 간 동기 호출 gRPC 전환

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 inventory 재고 조회 클라이언트를 REST 호출로 되돌린다. proto에 정의된 RPC는 `GetStock` 하나뿐이고 외부 API는 REST를 그대로 쓰고 있어 되돌릴 범위가 작다. 단, 저장소에 서비스 코드가 없어서 REST 재고 조회 엔드포인트가 아직 남아 있는지는 확인하지 못했다. 되돌리면 피크 시간 p99 SLO 초과가 다시 생긴다.
- **Migration Cost:** Low

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 다시 검토한다.

## References

- **Documentation:** `docs/decisions.md` D-007 (원본 결정 로그, 담당: 플랫폼팀), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto`, 커밋 c32c6dc (feat(inventory): gRPC 재고 조회 엔드포인트), 102695e (docs: gRPC 부하테스트 결과 추가)
