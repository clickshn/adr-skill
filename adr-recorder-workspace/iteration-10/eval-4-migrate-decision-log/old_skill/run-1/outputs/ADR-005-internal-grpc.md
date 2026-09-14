# ADR-005: 서비스 간 내부 통신 REST → gRPC 전환

- **Status:** Accepted
- **Date:** 2026-03-02
- **Decision:** 내부 서비스 간 동기 호출은 gRPC(protobuf)로 전환하고, 외부 공개 API는 REST를 유지한다.
- **Scope:** checkout-platform — 서비스 간 내부 동기 통신 (담당: 플랫폼팀)
- **Decision Source:** Human

---

## Context

### Problem

checkout → inventory 재고 조회 호출이 주문당 평균 6회 발생한다. REST+JSON 직렬화 비용 때문에 피크 시간 p99 지연이 SLO(100ms)를 초과했다.

### Constraints

- 외부 공개 API는 REST를 유지해야 한다.
- 플랫폼팀 인원이 2명이라 스키마 관리나 게이트웨이 운영 부담이 큰 방식은 감당하기 어렵다.
- 재고 데이터는 실시간성이 필요하다.

## Decision

### Selected

- **Technology:** gRPC + Protocol Buffers (proto3)
- **Architecture:** 내부 서비스 간 동기 호출은 gRPC를 쓰고, 외부 공개 API는 REST를 유지한다.
- **Implementation:** 2026-03-02부터 checkout ↔ inventory 구간에서 시행 중이다. 계약 정의는 `proto/inventory.proto`에 있다(`inventory.v1.InventoryService.GetStock`: `GetStockRequest{sku}` → `GetStockResponse{sku, quantity}`).

## Rationale

1. 사내 부하테스트에서 checkout → inventory 재고 조회의 p99가 180ms에서 52ms로 줄어 SLO(100ms) 안으로 들어왔다.
2. 평균 페이로드 크기가 약 60% 줄었다(4.8KB → 1.9KB).
3. 외부 공개 API는 REST로 두어 전환 범위를 내부 동기 호출로 한정했다.

## Evidence

- **Benchmark:** `bench/grpc-loadtest-2026-02.md` (2026-02-18, k6 500 VU, 10분, checkout → inventory 재고 조회) — REST+JSON 대비 gRPC: p50 41ms → 12ms, p99 180ms → 52ms, 평균 페이로드 4.8KB → 1.9KB(약 60% 감소). 원본 로그(D-007)에 적힌 "p99 45ms"는 커넥션 풀 워밍업이 빠진 1차 측정(2026-02-11) 값이다. 벤치 문서가 최종값으로 명시한 52ms를 여기에 적는다.

## Alternatives

### GraphQL 페더레이션

- **Cons:** 스키마 관리와 게이트웨이 운영 부담이 크다.
- **Rejected because:** 현 인원(플랫폼팀 2명)으로는 감당할 수 없다.
- **Recheck if:** 플랫폼팀이 4명 이상으로 늘어난다.

### REST 유지 + 응답 캐싱

- **Cons:** 재고 데이터는 실시간성이 필요해 캐시 무효화가 어렵다.
- **Rejected because:** 재고 데이터의 실시간성 요구 때문에 캐시 무효화가 어렵다.

## Consequences

### Positive

- checkout → inventory 재고 조회 p99가 부하테스트 기준 SLO(100ms) 안으로 들어온다.
- 호출당 페이로드가 약 60% 줄어든다.

### Negative

- 내부(gRPC)와 외부(REST) 두 프로토콜을 함께 운영해야 한다.
- 서비스 간 계약을 protobuf 스키마(`proto/`)로 관리해야 한다.

### Risks

- 근거 수치는 사내 부하테스트 값이고 프로덕션 실측은 아니다. 원본 로그의 p99 수치(45ms)가 벤치 최종값(52ms)과 달라 인용할 때 혼동될 수 있다.

## Implementation

- [x] 구현 작업: checkout ↔ inventory 구간 gRPC 전환 (2026-03-02 시행, `proto/inventory.proto`)
- [ ] 구현 작업: 그 밖의 내부 서비스 간 동기 호출 전환 (원본 로그에 대상과 일정 기록 없음)
- [x] 테스트: k6 부하테스트 (`bench/grpc-loadtest-2026-02.md`)
- [ ] 모니터링: 원본 로그에 기록 없음
- [ ] 문서/설정 업데이트: 원본 로그에 기록 없음

## Reversibility

- **Reversible:** Yes
- **Rollback:** checkout → inventory 호출을 REST+JSON으로 되돌린다. 되돌리면 부하테스트 기준 p99가 180ms로 돌아가 SLO 초과 문제가 재발한다. 저장소에는 `proto/inventory.proto`만 있고 REST 엔드포인트 코드는 없어서, 기존 REST 경로가 아직 남아 있는지는 확인하지 못했다.
- **Migration Cost:** Low — 현재 전환된 것은 checkout ↔ inventory 구간 1개, RPC 1개(`GetStock`)뿐이다. 다른 내부 호출이 전환될수록 비용이 커진다.

## Review Trigger

- 플랫폼팀이 4명 이상으로 늘어나면 GraphQL 페더레이션을 재검토한다.

## References

- **Documentation:**
  - `docs/decisions.md` D-007 (이관 원본)
  - `bench/grpc-loadtest-2026-02.md`
  - `proto/inventory.proto`
  - 커밋 `919fb33` feat(inventory): gRPC 재고 조회 엔드포인트
  - 커밋 `4b0137d` docs: gRPC 부하테스트 결과 추가
