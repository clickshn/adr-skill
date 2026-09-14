# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform — 내부 서비스 간 동기 호출 (현재 시행 구간: checkout ↔ inventory)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- p99 지연 SLO 100ms
- 외부 공개 API는 REST 유지
- 플랫폼팀 운영 인원 2명 (스키마·게이트웨이 운영 여력 제한)
- 재고 데이터는 실시간성이 필요함

## Decision

### Selected

- **Technology:** gRPC (protobuf, proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST 유지
- **Implementation:** `proto/inventory.proto` (package `inventory.v1`, `InventoryService.GetStock`: sku → quantity). 2026-03-02부터 checkout ↔ inventory 구간 시행 중. 담당: 플랫폼팀.

## Rationale

1. 사내 부하테스트에서 checkout → inventory 재고 조회 p99가 SLO(100ms) 안으로 들어왔다 (180ms → 52ms, Evidence 참조).
2. 페이로드 크기가 약 60% 줄어 직렬화 비용이 감소했다.
3. 대안인 GraphQL 페더레이션은 현 인원으로 운영이 불가하고, REST+캐싱은 재고 실시간성 때문에 캐시 무효화가 어렵다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (2026-02-18, k6 500 VU 10분, checkout → inventory 재고 조회): REST+JSON 대비 gRPC p50 41ms → 12ms, p99 180ms → 52ms, 평균 페이로드 4.8KB → 1.9KB (약 60% 감소). 원본 D-007에 적힌 p99 45ms는 커넥션 풀 워밍업을 빠뜨린 1차 측정(2026-02-11) 값이고, 벤치 문서의 최종값은 52ms다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리·게이트웨이 운영 부담
- **Rejected because:** 현 인원(플랫폼팀 2명)으로 운영 부담을 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘면

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려움
- **Rejected because:** 재고 실시간성 요구로 캐시 무효화 문제를 해결하기 어려움

## Consequences

### Positive

- checkout → inventory 재고 조회 p99가 벤치 기준 SLO(100ms) 이내 (52ms)
- 페이로드 약 60% 감소

### Negative

- 내부(gRPC)와 외부(REST) 두 프로토콜을 함께 운영해야 함
- `.proto` 스키마 정의·버전 관리가 필요함

### Risks

- 근거 수치는 벤치 결과뿐이다. 시행(2026-03-02) 이후 운영 환경 p99 실측치는 기록되어 있지 않다.

## Implementation

- [x] `proto/inventory.proto` 정의 (`InventoryService.GetStock`)
- [x] checkout ↔ inventory 구간 전환 (2026-03-02부터 시행)
- [ ] 나머지 내부 서비스 간 동기 호출 전환 (원본에 대상 구간·일정 기록 없음)

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 inventory 호출을 REST 클라이언트로 되돌린다. 저장소에는 `proto/inventory.proto`만 있고 서비스 코드가 없어서 inventory의 REST 엔드포인트가 아직 남아 있는지는 확인할 수 없다. 되돌리면 벤치 기준 p99 180ms로 SLO 초과가 다시 생긴다.
- **Migration Cost:** Low (현재 시행 범위인 checkout ↔ inventory, RPC 1개 기준. 전환 구간이 늘면 커진다.)

## Review Trigger

- GraphQL 페더레이션: 플랫폼팀이 4명 이상으로 늘면 재검토

## References

- **Documentation:** `docs/decisions.md` (D-007, 원본 결정 로그), `bench/grpc-loadtest-2026-02.md`, `proto/inventory.proto` — 파일이 실제로 추가된 커밋은 979e62c. gRPC 관련 메시지를 가진 커밋 919fb33(`feat(inventory): gRPC 재고 조회 엔드포인트`)과 4b0137d(`docs: gRPC 부하테스트 결과 추가`)에는 파일 변경이 없다.
