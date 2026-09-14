# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform 내부 서비스 간 동기 통신 (현재 checkout ↔ inventory 구간 시행 중, 담당: 플랫폼팀)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 넘었다.

### Constraints

- p99 지연 SLO 100ms
- 플랫폼팀 인원 2명이라 운영 부담이 큰 방식은 감당할 수 없음
- 재고 데이터는 실시간성이 필요함
- 외부 공개 API는 REST 유지

## Decision

### Selected

- **Technology:** gRPC (protobuf)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC, 외부 공개 API는 REST
- **Implementation:** 2026-03-02부터 checkout ↔ inventory 구간 시행 중. `proto/inventory.proto`에 `inventory.v1.InventoryService/GetStock` 정의

## Rationale

1. 사내 부하테스트에서 checkout → inventory 재고 조회 p99가 180ms → 52ms로 줄어 SLO(100ms)를 충족한다.
2. 평균 페이로드 크기가 약 60% 줄어(4.8KB → 1.9KB) 문제 원인이던 REST+JSON 직렬화 비용이 줄어든다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (2026-02-18, k6 500 VU 10분, checkout → inventory 재고 조회) — REST+JSON p50 41ms / p99 180ms / 평균 페이로드 4.8KB, gRPC p50 12ms / p99 52ms / 1.9KB. 원본 D-007에는 p99 45ms로 적혀 있으나, 이 값은 커넥션 풀 워밍업이 누락된 1차 측정(2026-02-11) 값이고 벤치 문서의 최종값은 52ms다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리·게이트웨이 운영 부담
- **Rejected because:** 현 인원(플랫폼팀 2명)으로는 그 운영 부담을 감당할 수 없음
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어날 때

### REST 유지 + 응답 캐싱

- **Rejected because:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어려움

## Consequences

### Positive

- checkout → inventory 재고 조회 p99가 SLO(100ms) 안으로 들어옴 (부하테스트 기준 52ms)
- 평균 페이로드 약 60% 감소

### Negative

- 내부(gRPC)와 외부(REST) 두 가지 통신 방식을 함께 운영해야 함
- 서비스 간 인터페이스를 proto 스키마(`proto/inventory.proto`)로 관리해야 함

### Risks

- 결정 범위는 내부 동기 호출 전체지만 현재 시행 구간은 checkout ↔ inventory뿐이라, 전환이 끝날 때까지 내부 통신에 REST와 gRPC가 섞여 있음

## Implementation

- [x] inventory gRPC 재고 조회 엔드포인트 (`proto/inventory.proto`)
- [x] 부하테스트 (`bench/grpc-loadtest-2026-02.md`)
- [x] checkout ↔ inventory 구간 시행 (2026-03-02~)
- [ ] checkout ↔ inventory 외 내부 동기 호출 구간 전환 (원본에 대상·일정 기록 없음)

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout의 재고 조회 호출을 inventory REST+JSON 호출로 되돌린다. 전환된 구간은 checkout ↔ inventory 하나(RPC `GetStock` 1개)이고 외부 공개 API는 REST 그대로라 영향이 없다. 되돌리면 p99 SLO 초과가 다시 생긴다. 저장소에 서비스 구현 코드가 없어서 inventory의 REST 엔드포인트가 아직 남아 있는지는 확인하지 못했다.
- **Migration Cost:** Low

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션 재검토

## References

- **Documentation:**
  - 원본 결정 로그: `docs/decisions.md` D-007 (2026-09-11 이관)
  - 부하테스트: `bench/grpc-loadtest-2026-02.md`
  - 커밋: adb2e90 (feat(inventory): gRPC 재고 조회 엔드포인트), 31a2593 (docs: gRPC 부하테스트 결과 추가) — 두 커밋 모두 파일 변경이 없고, `proto/inventory.proto`와 `bench/grpc-loadtest-2026-02.md`는 실제로 b1e5947에서 추가됨
